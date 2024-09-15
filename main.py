from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from langchain.schema import Document
from rag import load_and_split_documents, create_vector_store, setup_rag_chain, ask_question
from rag_mysql import insert_documents_and_vectors, CustomRetriever, setup_database_rag_chain
from load_config import read_json_config
import uvicorn
import os

app = FastAPI()

class Request(BaseModel):
    question: str

class Public:
    def __init__(self) -> None:
        # step 1: load config
        config = read_json_config("./documents/config.json")

        # step 2: load documents and pre operations
        # self.docs = load_and_split_documents()

        # step 3: creating vectorDB
        # self.vector_store = create_vector_store(config, self.docs)

        # step 4: creating the index and the chain
        # self.chain = setup_rag_chain(config, self.vector_store)

        # step 5: insert documents and vectors into the database
        # insert_documents_and_vectors(self.docs)
        
        # step 6:create custom retriever
        self.retriever = CustomRetriever()

        # step 7: create database chain
        self.database_chain = setup_database_rag_chain(config, self.retriever)

public = Public()

@app.post("/query/")
async def query(request: Request):
    response = ask_question(public.chain, request.question)
    return {"response": response['result']}

@app.post("/query_endpoint/", response_class=HTMLResponse)
async def query_endpoint(question: str = Form(...)):
    response = ask_question(public.database_chain, question)
    query = response['query']
    result = response['result']
    html_content = """
    <html>
        <head>
            <title>Answer your question</title>
        </head>
        <body>
            <h1>Answer your question</h1>
            <p>Your question: {query} </p>
            <p>Answer: {rresult} </p>
        </body>
    </html>
    """

    return HTMLResponse(content=html_content.format(query=query, rresult=result), status_code=200)

@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = """
    <html>
        <head>
            <title>Ask your question</title>
        </head>
        <body>
            <h1>Ask your question</h1>
            <form action="/query_endpoint/" method="post">
                <label for="question">Question:</label>
                <input type="text" id="question" name="question">
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port, reload=True)
