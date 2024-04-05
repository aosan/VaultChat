#!/usr/bin/env python3
import os
import argparse
import time
import chromadb
from dotenv import load_dotenv
from chromadb.config import Settings
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
import logging

# Load environment variables from .env file
load_dotenv()

# Constants and configurations
MODEL = os.getenv("LLM_MODEL_NAME", "mistral")
EMBEDDINGS_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
SOURCE_DIRECTORY = os.getenv('SOURCE_DIRECTORY', 'private_documents')
PERSIST_DIRECTORY = os.getenv("PERSISTENT_DATABASE", "chroma_db")
ANONYMIZE_TELEMETRY = os.getenv('ANONYMIZE_TELEMETRY', 'True') == 'True'
TARGET_SOURCE_CHUNKS = int(os.getenv('TARGET_SOURCE_CHUNKS', 5))


# Define anonymize telemetry for Chroma DB
client = chromadb.Client(Settings(anonymized_telemetry=ANONYMIZE_TELEMETRY))

def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Parse the command line arguments
    args = parse_arguments()
    
    # Initialize embeddings and database
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)
    db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": TARGET_SOURCE_CHUNKS})
    
    # Initialize callback handlers
    callbacks = [StreamingStdOutCallbackHandler()] if args.streaming else []
    llm = Ollama(model=MODEL, callbacks=callbacks)

    # Setup RetrievalQA chain
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=not args.hide_source)

    # Initialize conversation history
    conversation_history = []

    # Run interactive Q&A
    interactive_qa(qa, args, conversation_history)

def interactive_qa(qa, args, history):
    # Usage instructions
    print(f"\n\033[31;47m>>> Ready for private chat. Exit the session by typing 'exit' or '/bye'\033[0m")
    """Run interactive question and answer session."""
    while True:
        query = input("\n\033[31;47m>>> Enter a question: \033[0m").strip().lower()  # Normalize the input to handle case-insensitivity
        
        if query in ["exit", "/bye"]:
            print("Exiting. Goodbye!")  
            break
        if not query:
            continue

        try:
            start = time.time()
            result = qa.invoke(query)
            end = time.time()

            print_answer(result, query, args, start, end) 
        except Exception as e:
            logging.error(f"Error processing query: {e}")

def print_answer(result, query, args, start, end):
    """Prints the answer and relevant sources with colored output for the source document indicator."""
    answer, docs = result['result'], [] if args.hide_source else result['source_documents']
    print(f"\n\n> Question: {query}\n{answer}") 
    # Color code for the source document line. You can change the color by modifying the ANSI code.
    color_code = "\033[94m"  # Bright blue color
    reset_code = "\033[0m"  # Resets the color to default
    for document in docs:
        # Apply color only to the line indicating the source document
        source_line = f"{color_code}> {document.metadata['source']}{reset_code}"
        print(f"\n{source_line}:\n{document.page_content}")
    print(f"\n >>> Processing time: {end - start:.2f} seconds")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='VaultChat: Ask questions about your documents via a LLM.')
    parser.add_argument("--hide-source", "-S", action='store_true', help='Disable printing of source documents used for answers.')
    # Use --streaming flag to enable streaming StdOut callback
    parser.add_argument("--streaming", action='store_true', help='Enable the streaming StdOut callback for LLMs.')
    return parser.parse_args()

if __name__ == "__main__":
    main()
