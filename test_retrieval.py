import os

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "kartease_policies"


# Create embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


# Connect to existing Chroma database
chroma_client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

vector_store = Chroma(
    client=chroma_client,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)


question = "What is the return window for phones?"

print(f"\nQuestion: {question}")
print("\nTop 3 retrieved chunks:\n")


results = vector_store.similarity_search_with_score(
    question,
    k=3,
)


for i, (document, score) in enumerate(results, start=1):
    print(f"--- Result {i} ---")
    print(f"Source: {document.metadata.get('source')}")
    print(f"Score: {score}")
    print(f"Content:\n{document.page_content}")
    print()