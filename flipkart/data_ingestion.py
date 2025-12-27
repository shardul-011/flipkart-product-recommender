import os
import hashlib
from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from flipkart.config import config
from flipkart.data_converter import DataConverter


class DataIngestion:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(
            model=config.Embedding_Model
        )

        self.vector_store = AstraDBVectorStore(
            api_endpoint=config.ASTRA_DB_API_ENDPOINT_KEY,
            token=config.ASTRA_DB_APPLICATION_TOKEN,
            namespace=config.ASTRA_DB_KEYSPACE,
            embedding=self.embedding,
            collection_name="flipkart_database"
        )

        self.data_dir = "data"

    def _content_hash(self, text: str) -> str:
        return hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()

    def ingest(self, load_existing=True):
        if load_existing:
            return self.vector_store

        documents = []
        ids = []

        for file_name in os.listdir(self.data_dir):
            if not file_name.endswith(".csv"):
                continue

            file_path = os.path.join(self.data_dir, file_name)
            docs = DataConverter(file_path).convert()

            for doc in docs:
                hash_id = self._content_hash(doc.page_content)

                doc.metadata["source_file"] = file_name
                doc.metadata["content_hash"] = hash_id

                documents.append(doc)
                ids.append(hash_id)  # 🔥 content-based ID

        if documents:
            self.vector_store.add_documents(
                documents=documents,
                ids=ids
            )

        return self.vector_store

