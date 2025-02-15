# Import necessary modules for RAG
from dotenv import load_dotenv, get_key
from chromadb import PersistentClient, Settings
from langchain.vectorstores import Chroma
from langchain_voyageai import VoyageAIEmbeddings

# Load environment variables
load_dotenv()
DEFAULT_TENANT = "default_tenant"
DEFAULT_DATABASE = "default_database"

# Set up the Chroma persistent client
client = PersistentClient(
    path="chroma_db",
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
    settings=Settings()
)

# Initialize VoyageAI embeddings using the API key from .env
embeddings = VoyageAIEmbeddings(
    voyage_api_key=get_key(dotenv_path=".env", key_to_get="VOYAGEAI_KEY"),
    model="voyage-large-2-instruct"
)

# Create the vector store instance
saved_data_store = Chroma(
    persist_directory="chroma_db",
    collection_name="umich_wn2025",  # Ensure this matches your collection
    embedding_function=embeddings,
    client=client
)

# Create retrievers (using similarity or mmr, as needed)
retriever_sim = saved_data_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 15, "score_threshold": 0.6}
)
retriever_mmr = saved_data_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 15}
)

def get_context_from_vector_db(query: str, use_mmr: bool = False) -> str:
    """
    Given a user query, retrieve relevant document chunks from the vector DB.
    You can choose between using similarity-based retrieval or mmr.
    Returns the concatenated context passages.
    """
    retriever = retriever_mmr if use_mmr else retriever_sim
    # Invoke the retriever to get a list of Document objects
    context_docs = retriever.invoke(query)
    # Combine the text from the documents into one context string
    context = "\n".join([doc.page_content for doc in context_docs])
    return context
