import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")


# Paths
DATA_DIR = "data"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "kartease_policies"


# --------------------------------------------------
# 1. Load policy documents
# --------------------------------------------------

print("Loading policy documents...")

loader = DirectoryLoader(
    DATA_DIR,
    glob="*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)

documents = loader.load()

print(f"Loaded {len(documents)} policy documents.")


# --------------------------------------------------
# 2. Split documents into chunks
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks.")


# --------------------------------------------------
# 3. Keep source filename in metadata
# --------------------------------------------------

for chunk in chunks:
    source = chunk.metadata.get("source", "")
    chunk.metadata["source"] = Path(source).name


# --------------------------------------------------
# 4. Create Gemini embedding model
# --------------------------------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


# --------------------------------------------------
# 5. Create / reuse Chroma database
# --------------------------------------------------

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

existing_collections = [
    collection.name for collection in chroma_client.list_collections()
]

if COLLECTION_NAME in existing_collections:
    collection = chroma_client.get_collection(COLLECTION_NAME)

    existing_count = collection.count()

    print(f"Chroma collection already exists with {existing_count} chunks.")

    if existing_count > 0:
        print("Skipping embedding. Existing vectors will be reused.")
        print("Ingestion complete.")
        exit()


# --------------------------------------------------
# 6. Store chunks in Chroma
# --------------------------------------------------

print("Creating embeddings and storing them in Chroma...")

vector_store = Chroma(
    client=chroma_client,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

vector_store.add_documents(chunks)

print(f"Stored {len(chunks)} chunks in Chroma.")
print("Ingestion complete!")