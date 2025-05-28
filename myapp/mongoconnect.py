import os
import uuid
import urllib.parse
import traceback

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class VectorSearchManager:
    def __init__(self, connection_string=None):
        """
        Initialize Vector Search Manager with robust configuration

        Args:
            connection_string (str, optional): MongoDB connection string
        """
        self.connection_string = connection_string or self._get_mongodb_connection_string()
        self.embeddings = None
        self.client = None

    def _get_mongodb_connection_string(self):
        """
        Generate MongoDB connection string with secure parsing

        Returns:
            str: Parsed and secured connection string
        """
        username = urllib.parse.quote_plus('kashishc')
        password = urllib.parse.quote_plus('5ytsbmd7dtsn9z33')
        cluster_url = 'cluster0.iz8ovwj.mongodb.net'

        return f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority&appName=Cluster0"

    def _generate_unique_name(self, prefix=''):
        """
        Generate unique identifier for database/collection names

        Args:
            prefix (str, optional): Prefix for the name

        Returns:
            str: Unique name
        """
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def load_documents(self, urls):
        """
        Load and split documents from given URLs

        Args:
            urls (list): List of URLs to load documents from

        Returns:
            list: Split documents
        """
        loaders = [WebBaseLoader(url) for url in urls]

        data = []
        for loader in loaders:
            data.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "(?<=\. )", " "],
            length_function=len
        )

        return text_splitter.split_documents(data)

    def prepare_embeddings(self, model_name="facebook/bart-base"):
        """
        Prepare embeddings using HuggingFace

        Args:
            model_name (str, optional): HuggingFace model name
        """
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={
                    'normalize_embeddings': True,
                    'batch_size': 32  # Efficient batch processing
                }
            )
        except Exception as e:
            print(f"Embedding Model Error: {e}")
            raise

    def connect_mongodb(self):
        """
        Establish MongoDB connection with advanced error handling
        """
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=15000,
                socketTimeoutMS=15000,
                connectTimeoutMS=15000,
                maxPoolSize=50,  # Connection pool size
                minPoolSize=10
            )

            # Comprehensive connection test
            self.client.admin.command('ismaster')
            print("✅ MongoDB Connection Established Successfully")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ MongoDB Connection Failed: {e}")
            print("Troubleshooting Recommendations:")
            print("1. Verify network connectivity")
            print("2. Check MongoDB Atlas credentials")
            print("3. Ensure IP whitelisting")
            traceback.print_exc()
            raise

    def store_vectors(self, documents):
        """
        Store vector embeddings in MongoDB Atlas

        Args:
            documents (list): Processed documents

        Returns:
            dict: Metadata about vector storage
        """
        if not self.embeddings or not self.client:
            raise ValueError("Embeddings or MongoDB connection not initialized")

        try:
            # Dynamic naming with secure generation
            db_name = self._generate_unique_name('vectordb')
            collection_name = self._generate_unique_name('documents')
            index_name = self._generate_unique_name('vector_index')

            db = self.client[db_name]
            collection = db[collection_name]

            # Clear existing documents
            collection.delete_many({})

            # Store vectors
            vector_store = MongoDBAtlasVectorSearch.from_documents(
                documents,
                self.embeddings,
                collection=collection,
                index_name=index_name
            )

            return {
                'db_name': db_name,
                'collection_name': collection_name,
                'index_name': index_name,
                'total_documents': collection.count_documents({})
            }

        except Exception as e:
            print(f"Vector Storage Error: {e}")
            traceback.print_exc()
            raise


def main():
    # URLs to load documents from
    document_urls = [
        "https://en.wikipedia.org/wiki/AT%26T",
        "https://en.wikipedia.org/wiki/Bank_of_America"
    ]

    try:
        # Initialize Vector Search Manager
        vsm = VectorSearchManager()

        # Load Documents
        documents = vsm.load_documents(document_urls)
        print(f"📄 Loaded and Split {len(documents)} Document Chunks")

        # Prepare Embeddings
        vsm.prepare_embeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Connect to MongoDB
        vsm.connect_mongodb()

        # Store Vectors
        result = vsm.store_vectors(documents)

        # Print Results
        print("\n🔍 Vector Storage Results:")
        for key, value in result.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    except Exception as e:
        print(f"❌ Workflow Execution Failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()