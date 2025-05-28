from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import os
import chromadb



load_dotenv()
openai_key=os.getenv("OPENAI_AI_KEY")

chroma_client = chromadb.PersistentClient(path="./knowledge_base")
collection_name = "FAQs"
collection = chroma_client.get_or_create_collection(collection_name)


def retriever(query):
    embedding_model = OpenAIEmbeddings(api_key=openai_key)
    query_embedding = embedding_model.embed_query(query)
    results= collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )
    return results

