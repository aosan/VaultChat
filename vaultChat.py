#!/usr/bin/env python3
import os
import argparse
import time
import chromadb
from dotenv import load_dotenv
from chromadb.config import Settings
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
import logging
from datetime import datetime

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
    print(f"\n\033[31;47m>>> Ready for private chat. Exit the session by typing 'exit' or '/bye'. Save the chat by typing '/save <summary_name>'.\033[0m")
    """Run interactive question and answer sessions with your private data."""
    while True:
        query = input("\n\033[31;47m>>> Enter a question: \033[0m").strip().lower()  # Normalize the input to handle case-insensitivity
        
        if query in ["exit", "/bye"]:
            print("Exiting. Goodbye!")  
            break
        elif query.startswith("/save"):
            save_chat_history(history, query)
            continue
        if not query:
            continue

        try:
            start = time.time()
            for output in qa_invoke_streaming(qa, query, history):
                print(output, end='', flush=True)
            end = time.time()

            print(f"\n >>> Processing time: {end - start:.2f} seconds")
        except Exception as e:
            logging.error(f"Error processing query: {e}")

def qa_invoke_streaming(qa, query, history):
    """Invoke the QA system with streaming output."""
    result = qa.invoke(query)
    history.append(f"### Question: {query}\n{result['result']}\n")
    
    yield f"\n\n> Question: {query}\n{result['result']}"
    
    if 'source_documents' in result:
        color_code = "\033[94m"  # Bright blue color
        reset_code = "\033[0m"  # Resets the color to default
        sources_text = ""
        for document in result['source_documents']:
            source_line = f"{color_code}> {document.metadata['source']}{reset_code}"
            source_content = f"{source_line}:\n{document.page_content}"
            sources_text += f"\n{source_content}"
            yield f"\n{source_content}"
        history[-1] += sources_text

# def save_chat_history(history, query):
#     """Save the chat history to a markdown file."""
#     try:
#         _, summary_name = query.split(maxsplit=1)
#         timestamp = datetime.now().strftime("%y%m%d%H%M")
#         file_name = f"{timestamp}_{summary_name.replace(' ', '_').lower()}.md"
#         with open(file_name, 'w') as f:
#             f.write("# Chat History\n\n")
#             f.writelines(history)
#         print(f"Chat history saved as {file_name}")
#     except ValueError:
#         print("Invalid command. Use /save <summary_name>")


def save_chat_history(history, query):
    """Save the chat history to a markdown file in the 'chats_history' folder."""
    try:
        # Create 'chats_history' folder if non-existent
        os.makedirs("chats_history", exist_ok=True)

        _, summary_name = query.split(maxsplit=1)
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        file_name = f"{timestamp}_{summary_name.replace(' ', '_').lower()}.md"
        file_path = os.path.join("chats_history", file_name)

        with open(file_path, 'w') as f:
            f.write("# Chat History\n\n")
            f.writelines(history)
        
        print(f"Chat history saved as {file_path}")
    except ValueError:
        print("Invalid command. Use /save <summary_name>")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='VaultChat: Ask questions about your documents via a LLM.')
    parser.add_argument("--hide-source", "-S", action='store_true', help='Disable printing of source documents used for answers.')
    parser.add_argument("--streaming", action='store_true', help='Enable the streaming from LLMs.')
    return parser.parse_args()

if __name__ == "__main__":
    main()
