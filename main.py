import os
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    Settings, 
    StorageContext, 
    load_index_from_storage
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from loaders.excel_loader import load_excel_documents


# 1. Setup the LLM (The Brain)
# We manually set context_window to bypass the automatic metadata network call
# that was causing your ConnectionError.
Settings.llm = Ollama(
    model="llama3.2:3b", 
    request_timeout=600.0,
    context_window=2048

)

# 2. Setup Local Embeddings (The Librarian)
# Uses your local machine memory, bypassing external network calls entirely.
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

def main():
   
    PERSIST_DIR = "./storage"
    DATA_DIR = "./data"

    # Check if we already have a saved index to avoid re-indexing
    if not os.path.exists(PERSIST_DIR):

        print("Creating index for the first time...")

        documents = load_excel_documents(DATA_DIR)

        index = VectorStoreIndex.from_documents(documents)

        index.storage_context.persist(
            persist_dir=PERSIST_DIR
        )
    else:
        # Load the existing index
        print("Loading index from disk...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    
    # 3. Create the Query Engine with Streaming
    query_engine = index.as_query_engine(
    streaming=True,
    similarity_top_k=3
)
    
    print("\n--- System Ready! ---")
    while True:
        user_query = input("\nAsk a question about your data (or 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break
            
        print("\nAI is thinking...")
        try:
            response = query_engine.query(user_query)
            print("\nResponse: ", end="")
            response.print_response_stream()
            print("\n")
        except Exception as e:
            print(f"\nAn error occurred during query: {e}")

if __name__ == "__main__":
    main()