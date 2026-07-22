from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama


# Configure the same models used during indexing
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

Settings.llm = Ollama(
    model="phi4",
    request_timeout=600,
    context_window=2048
)


class RAGTool:

    def __init__(self):

        storage_context = StorageContext.from_defaults(
            persist_dir="./storage"
        )

        self.index = load_index_from_storage(
            storage_context
        )

        self.query_engine = self.index.as_query_engine(
            similarity_top_k=3
        )

    def run(self, query):

        response = self.query_engine.query(query)

        return str(response)