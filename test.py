import langchain

print("LangChain version:", langchain.__version__)
import sqlite3, chromadb
from sentence_transformers import SentenceTransformer
print("SQLite OK:", sqlite3.sqlite_version)
print("Chroma OK:", chromadb.__version__)
print("Embeddings OK:", SentenceTransformer('all-MiniLM-L6-v2'))
