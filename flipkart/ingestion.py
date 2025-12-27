from flipkart.data_ingestion import DataIngestion

if __name__ == "__main__":
    DataIngestion().ingest(load_existing=False)
    print("✅ Ingestion completed successfully")
