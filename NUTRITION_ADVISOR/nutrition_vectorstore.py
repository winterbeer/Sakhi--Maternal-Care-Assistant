from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, UnstructuredPDFLoader
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Custom loader for OCR fallback
def custom_loader(file_path: Path):
    try:
        return PyPDFLoader(str(file_path))
    except Exception as e:
        print(f"Standard PDF parse failed for {file_path}, using OCR: {e}")
        return UnstructuredPDFLoader(str(file_path), strategy="hi_res")

# Load documents
loader = DirectoryLoader(
    path="NUTRITION_ADVISOR",
    glob="*.pdf",
    loader_cls=custom_loader,
)

docs = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# Embed and persist vectorstore
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="NUTRITION_ADVISOR/vector_store"
)

vectorstore.persist()
