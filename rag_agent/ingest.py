import asyncio
from langchain_community.document_loaders import PyPDFLoader 
import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_openai import OpenAIEmbeddings

load_dotenv()
app= FastAPI()

openai_key=os.getenv("OPENAI_AI_KEY")
if not openai_key:
    raise ValueError("OPENAI_AI_KEY is not set or accessible!")

print(f"Using OpenAI API Key: {openai_key[:5]}...") 

chroma_client = chromadb.PersistentClient(path="./knowledge_base")
collection_name="FAQs"
collection = chroma_client.get_or_create_collection(collection_name)

async def load_multiple_pdfs(file_paths):
    all_pages = []
    for file_path in file_paths:
        try:
            loader = PyPDFLoader(file_path)
            pages = await loader.aload()  
            all_pages.extend(pages)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return all_pages

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  
    chunk_overlap=200,  
    length_function=len,
)


def generate_store_embeddings(chunks):
    embedding_model = OpenAIEmbeddings(api_key=openai_key)
    embeddings = embedding_model.embed_documents(chunks)
    for chunk_id, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{"source": "knowledge_base"}],
            ids=[str(chunk_id)] 
        )

async def initialize_knowledge_base():
    pdf_files = ['test1.pdf', 'test2.pdf','test3.pdf']  
    try:
        pages = await load_multiple_pdfs(pdf_files)
    except Exception as e:
        print(f"Error loading PDFs: {e}")
        return
    chunks = []
    for page in pages:
        chunks.extend(text_splitter.split_text(page.page_content))
        
    generate_store_embeddings(chunks)          



if __name__ == "__main__":
    asyncio.run(initialize_knowledge_base())
   


  




        

