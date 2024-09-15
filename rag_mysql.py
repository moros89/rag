from db_connection import public_db_connection
from embeddings import public_embeddings
from load_config import read_json_config
from rag import load_and_split_documents, ask_question
import numpy as np
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_core.retrievers import BaseRetriever
from langchain.chains import RetrievalQA

#Insert documents and vectors into the database
def insert_documents_and_vectors(docs):
    cursor = public_db_connection.cursor()

    for doc in docs:
        vector = public_embeddings.embed_documents([doc.page_content])[0]
        vector_blob = np.array(vector).tobytes()
        cursor.execute("INSERT INTO documents (content, vector) VALUES (%s, %s)", (doc.page_content, vector_blob))

    cursor.close()
    public_db_connection.commit()

# Retrieve vectors from the database
def retrieve_vectors(query_vector, top_k = 5):
    cursor = public_db_connection.cursor()
    cursor.execute("SELECT id, vector FROM documents")
    rows = cursor.fetchall()
    query_vector = np.array(query_vector)

    distances = []
    for doc_id, vector_blob in rows:
        vector = np.frombuffer(vector_blob, dtype = np.float64)
        reminds = query_vector - vector
        distance = np.linalg.norm(reminds)
        distances.append((doc_id, distance))

    distances.sort(key = lambda x: x[1])
    return [doc_id for doc_id, distance in distances[:top_k]]

def query_tag_chain(question):
    query_vector = public_embeddings.embed_query(question)
    similar_doc_ids = retrieve_vectors(query_vector)

    cursor = public_db_connection.cursor()
    query = "SELECT content FROM documents WHERE id IN (%s)" % (','.join(['%s'] * len(similar_doc_ids)))

    cursor.execute(query, tuple(similar_doc_ids))
    similar_docs = cursor.fetchall()

    documents = []
    for doc in similar_docs:
        doc = Document(page_content = doc[0])
        documents.append(doc)

    return documents

class CustomRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str, top_k = 5):
        documents = query_tag_chain(query)
        return documents[:top_k] 
    

def setup_database_rag_chain(config, rettriever):
    llm = ChatOpenAI(
        api_key = config["api_key"],
        base_url = config["base_url"]
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm = llm,
        chain_type = "stuff",
        retriever = rettriever
    )

    return rag_chain

if __name__ == "__main__":
    config = read_json_config("./documents/config.json")
    documents = load_and_split_documents()
    insert_documents_and_vectors(documents)
    rettriever = CustomRetriever()
    rag_chain = setup_database_rag_chain(config, rettriever)
    
    query = "What is the capital of France?"
    response = ask_question(rag_chain, query)
    print(response['result'])

    query = "What is the main topic of this document?"
    response = ask_question(rag_chain, query)
    print(response['result'])