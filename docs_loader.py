#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import markdown
import chromadb
from chromadb.config import Settings
import glob
from typing import List
from multiprocessing import Pool
from tqdm import tqdm
import logging

# Load environment variables from .env file
load_dotenv() 

# Configure logging
logging.basicConfig(level=logging.INFO, filename='document_processing.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

from langchain_community.document_loaders import (
    UnstructuredFileLoader,
    CSVLoader,
    EverNoteLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load environment variables
default_num_processes = os.getenv('DEFAULT_NUM_PROCESSES')
persist_directory = os.getenv('PERSISTENT_DATABASE', 'chroma_db')
anonymize_telemetry = os.getenv('ANONYMIZE_TELEMETRY', 'True') == 'True'
source_directory = os.getenv('SOURCE_DIRECTORY', 'private_documents')
embeddings_model_name = os.getenv('EMBEDDINGS_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')
documents_batch_size = int(os.getenv('DOCUMENTS_BATCH_SIZE', 200))
embeddings_batch_size = int(os.getenv('BATCH_SIZE', 5461))
chunk_size = int(os.getenv('CHUNK_SIZE', 500))
chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 3))
max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', 200))

# Define anonymize telemetry for Chroma DB
client = chromadb.Client(Settings(anonymized_telemetry=anonymize_telemetry))

def submit_embeddings_in_batches(embeddings, texts, metadatas, ids, chroma_collection, batch_size=embeddings_batch_size):
    total_batches = (len(embeddings) + batch_size - 1) // batch_size
    for i in tqdm(range(total_batches), desc="Submitting Embeddings", ncols=80):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, len(embeddings))
        batch_embeddings = embeddings[start_idx:end_idx]
        batch_texts = texts[start_idx:end_idx] if texts else None
        batch_metadatas = metadatas[start_idx:end_idx] if metadatas else None
        batch_ids = ids[start_idx:end_idx] if ids else None
        chroma_collection.add_texts(texts=batch_texts, embeddings=batch_embeddings, metadatas=batch_metadatas, ids=batch_ids)

class ElmLoader(UnstructuredEmailLoader):
    def load(self) -> List[UnstructuredFileLoader]:
        try:
            docs = super().load()  
        except ValueError as e:
            if 'text/html content not found in email' in str(e):
                self.unstructured_kwargs["content_source"] = "text/plain"
                docs = super().load()  # Retry loading with updated kwargs
            else:
                raise
        except Exception as e:
            raise type(e)(f"{self.file_path}: {e}") from e

        return docs

# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".eml": (ElmLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    ".md": (UnstructuredMarkdownLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}

# Create console handler and set level to warning, so we can scare the cats
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the root logger
logging.getLogger('').addHandler(console_handler)

def validate_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        logging.warning(f"File does not exist: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    
    # Check if the file is an empty promise
    if file_size == 0:
        logging.warning(f"Skipping empty file: {file_path}")
        return False
    
    # Check for file size, just in case...
    max_file_size_bytes = max_file_size_mb * 1024 * 1024
    if file_size > max_file_size_bytes:
        logging.warning(f"File too large (over {max_file_size_mb}MB): {file_path}")
        return False
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Ensure the file extension is supported
    if file_extension not in LOADER_MAPPING:
        logging.warning(f"Unsupported file extension '{file_extension}' for file: {file_path}")
        return False

    return True

def load_single_document(file_path: str) -> List[UnstructuredFileLoader]:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        if not validate_file(file_path):
            log_message = f"Skipped the loading of invalid file: {file_path}"
            print(log_message)
            logging.warning(log_message)  
            return []
        
        loader_class, loader_args = LOADER_MAPPING[ext]
        try:
            loader = loader_class(file_path, **loader_args)
            return loader.load()
        except Exception as e:
            log_message = f"Error loading file {file_path}: {e}"
            print(log_message)
            logging.error(log_message, exc_info=True)  
            return []  

    log_message = f"Unsupported file extension '{ext}' for file: {file_path}"
    print(log_message)
    logging.warning(log_message)  
    return []

def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[UnstructuredFileLoader]:
    all_files = []
    for ext in LOADER_MAPPING:
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
        )
    filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]

    # keep track of the definition source
    process_source = ""

    if default_num_processes and default_num_processes.isdigit():
        num_processes = int(default_num_processes)
        process_source = ".env"
    else:
        num_processes = os.cpu_count()
        process_source = "CPU discovery"

    # Display the number of processes used and their definition source
    print(f"Number of processes used: {num_processes} (defined by {process_source})")

    # Create a Pool with the determined number of processes
    with Pool(processes=num_processes) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
            for i, docs in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
                results.extend(docs)
                pbar.update()

    return results

def process_documents(ignored_files: List[str] = []) -> List[UnstructuredFileLoader]:
    """
    Load documents and split in chunks
    """
    print(f"Loading documents from {source_directory}")
    documents = load_documents(source_directory, ignored_files)
    if not documents:
        print("No new documents to load")
        exit(0)
    print(f"Loaded {len(documents)} new documents from {source_directory}")
    
  # Adjust as needed
    document_batches = [documents[i:i+documents_batch_size] for i in range(0, len(documents), documents_batch_size)]

    # Process each batch of documents
    processed_texts = []
    for batch in tqdm(document_batches, desc='Processing document batches', ncols=80):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(batch)
        processed_texts.extend(texts)
    
    print(f"Split into {len(processed_texts)} chunks of text (max. {chunk_size} tokens each)")
    return processed_texts

# check if Chroma store exists
def does_vectorstore_exist(persist_directory: str) -> bool:
    return os.path.exists(os.path.join(persist_directory, 'chroma.sqlite3'))

def main():
    
    # Check if the source_directory exists and is accessible
    if not os.path.isdir(source_directory):
        logging.error(f"source_directory does not exist: {source_directory}")
        print(f"Error: Documents directory does not exist: {source_directory}")
        exit(1)
    elif not os.access(source_directory, os.R_OK):
        logging.error(f"source_directory is not accessible: {source_directory}")
        print(f"Error: Documents directory is not accessible: {source_directory}")
        exit(1)
                         
    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    if does_vectorstore_exist(persist_directory):
        # Update and store locally vectorstore
        print(f"Appending existing vectorstore to {persist_directory}")
        
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        collection = db.get()
        texts = process_documents([metadata['source'] for metadata in collection['metadatas']])
        print(f"Creating embeddings. Please wait...")
        
        # Calculate the total number of batches
        total_batches = (len(texts) + embeddings_batch_size - 1) // embeddings_batch_size
        
        # Process texts in batches with tqdm for progress tracking
        for i in tqdm(range(total_batches), desc="Creating embeddings", ncols=80):
            batch_texts = texts[i*embeddings_batch_size : (i+1)*embeddings_batch_size]
            db.add_documents(batch_texts)
    else:
        # Create and store locally vectorstore
        print(f"Creating new vectorstore in {persist_directory}")
        texts = process_documents()
        print(f"Creating embeddings. Please wait...")
        
        # Calculate the total number of batches
        total_batches = (len(texts) + embeddings_batch_size - 1) // embeddings_batch_size
        
        # Initialize db outside of the loop to avoid reinitializing it for each batch
        db = None

        # Process texts in batches with tqdm for progress tracking
        for i in tqdm(range(total_batches), desc="Creating embeddings", ncols=80):
            batch_texts = texts[i*embeddings_batch_size : (i+1)*embeddings_batch_size]
            if db is None:
                db = Chroma.from_documents(batch_texts, embeddings, persist_directory=persist_directory)
            else:
                db.add_documents(batch_texts)
                
        if db is not None:
            db.persist()

    print(f"Documents are ready! You can now run vaultChat.py to query your model with your private documents")


if __name__ == "__main__":
    main()
