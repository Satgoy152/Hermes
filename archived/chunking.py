import os
import glob
import pandas as pd
import PyPDF2
from dotenv import load_dotenv, get_key
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from chromadb import PersistentClient, Settings
from langchain.vectorstores import Chroma
from langchain_voyageai import VoyageAIEmbeddings  # adjust the import as per your package

# Load environment variables from .env
load_dotenv()
VOYAGEAI_KEY = get_key(dotenv_path=".env", key_to_get="VOYAGEAI_KEY")

def load_documents_from_directory(directory):
    """
    Load documents from a directory. Supports TXT, CSV, and PDF files.
    Returns a list of Document objects with page_content and metadata.
    """
    documents = []
    for filepath in glob.glob(os.path.join(directory, "*")):
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append(Document(page_content=content, metadata={"source": filepath}))
        elif ext == ".csv":
            # Read CSV with pandas and convert to CSV string
            df = pd.read_csv(filepath)
            content = df.to_csv(index=False)
            documents.append(Document(page_content=content, metadata={"source": filepath}))
        elif ext == ".pdf":
            content = ""
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
            documents.append(Document(page_content=content, metadata={"source": filepath}))
        # Extend for other file types if needed.
    return documents

# Load all documents from the specified directory
docs_directory = "./rag_docs"
documents = load_documents_from_directory(docs_directory)

# Initialize a RecursiveCharacterTextSplitter for chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Adjust chunk size as needed
    chunk_overlap=200     # Overlap helps maintain context between chunks
)

# Loop through each document and split it into chunks
combined_chunks = []
for doc in documents:
    chunks = text_splitter.split_text(doc.page_content)
    for chunk in chunks:
        # Each chunk is stored as a Document with the original metadata
        combined_chunks.append(Document(page_content=chunk, metadata=doc.metadata))

# Set up the persistent Chroma client
DEFAULT_TENANT = "default_tenant"
DEFAULT_DATABASE = "default_database"
new_client = PersistentClient(
    path="./chroma_db",
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
    settings=Settings()
)

# Initialize VoyageAIEmbeddings with the API key and desired model
embeddings = VoyageAIEmbeddings(
    voyage_api_key=VOYAGEAI_KEY,
    model="voyage-large-2-instruct"
)

# Create a Chroma vector store from the chunked documents
vectorstore = Chroma.from_documents(
    documents=combined_chunks,
    embedding=embeddings,
    collection_name="umich_wn2025",
    client=new_client
)

print("Vector store created successfully with", len(combined_chunks), "chunks.")