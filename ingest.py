import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

DOCS_FOLDER = Path("documents")
DB_FOLDER = "chroma_db"

# 1. Load every PDF page
pages = []
for pdf in DOCS_FOLDER.glob("*.pdf"):
    title = pdf.stem.replace("IronStore_", "").replace("_", " ")
    for page in PyMuPDFLoader(str(pdf)).load():
        page.metadata["title"] = title
        pages.append(page)

# 2. Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(pages)
print(f"Loaded {len(pages)} pages, made {len(chunks)} chunks")

# 3. Save to Chroma (start fresh each time)
shutil.rmtree(DB_FOLDER, ignore_errors=True)
Chroma.from_documents(
    chunks,
    OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory=DB_FOLDER,
    collection_metadata={"hnsw:space": "cosine"},
)
print("Database saved to chroma_db/")