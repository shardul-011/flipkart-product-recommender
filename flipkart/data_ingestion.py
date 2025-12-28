import os
import time
import hashlib
from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from flipkart.config import config
from flipkart.data_converter import DataConverter
from utils.logger import get_logger


logger = get_logger(__name__)


class DataIngestion:
    def __init__(self):
        # ✅ Local embedding model (no API, no quota issues)
        self.embedding = HuggingFaceEmbeddings(
            model_name=config.Embedding_Model
        )

        # ✅ Astra DB vector store
        self.vector_store = AstraDBVectorStore(
            api_endpoint=config.ASTRA_DB_API_ENDPOINT_KEY,
            token=config.ASTRA_DB_APPLICATION_TOKEN,
            namespace=config.ASTRA_DB_KEYSPACE,
            embedding=self.embedding,
            collection_name="flipkart_database"
        )

        self.data_dir = "data"

        # 🔥 IMPORTANT TUNING
        self.BATCH_SIZE = 16
        self.MAX_RETRIES = 3

    def _content_hash(self, text: str) -> str:
        """Generate deterministic ID to avoid duplicates"""
        return hashlib.md5(
            text.strip().lower().encode("utf-8")
        ).hexdigest()

    def _safe_insert(self, documents, ids):
        """Insert with retry to handle network/DNS failures"""
        for attempt in range(self.MAX_RETRIES):
            try:
                self.vector_store.add_documents(
                    documents=documents,
                    ids=ids
                )
                logger.info(f"Inserted batch of {len(documents)} documents")
                return
            except Exception as e:
                logger.warning(
                    f"Astra insert failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}"
                )
                time.sleep(5)

        raise RuntimeError("Astra insert failed after maximum retries")

    def ingest(self, load_existing: bool = True):
        if load_existing:
            logger.info("Using existing Astra DB vector store")
            return self.vector_store

        documents = []
        ids = []
        total_docs = 0

        logger.info("Starting data ingestion")

        for file_name in os.listdir(self.data_dir):
            if not file_name.endswith(".csv"):
                continue

            file_path = os.path.join(self.data_dir, file_name)
            logger.info(f"Processing file: {file_name}")

            docs = DataConverter(file_path).convert()

            for doc in docs:
                hash_id = self._content_hash(doc.page_content)

                # Metadata (even if already present, this is safe)
                doc.metadata["source_file"] = file_name
                doc.metadata["content_hash"] = hash_id

                documents.append(doc)
                ids.append(hash_id)
                total_docs += 1

                # 🔥 Batch flush
                if len(documents) >= self.BATCH_SIZE:
                    self._safe_insert(documents, ids)
                    documents.clear()
                    ids.clear()

        # 🔥 Final flush (remaining docs)
        if documents:
            self._safe_insert(documents, ids)

        logger.info(f"Ingestion completed. Total documents processed: {total_docs}")

        return self.vector_store
