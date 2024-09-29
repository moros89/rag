from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain.schema import Document
from rag import load_and_split_documents, create_vector_store, setup_rag_chain, ask_question
from rag_mysql import insert_documents_and_vectors, CustomRetriever, setup_database_rag_chain
from load_config import public_config
from db_connection import query_users
import uvicorn
import os

app = FastAPI()

template = Jinja2Templates(directory="templates")

class Request(BaseModel):
    question: str

class Public:
    def __init__(self) -> None:
        # step 1: load config
        # config = read_json_config("./documents/config.json")

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
        self.database_chain = setup_database_rag_chain(public_config, self.retriever)

public = Public()

@app.post("/query")
async def query(request: Request):
    response = ask_question(public.chain, request.question)
    return {"response": response['result']}

@app.post("/query_endpoint", response_class=HTMLResponse)
async def query_endpoint(question: str = Form(...)):
    response = ask_question(public.database_chain, question)
    query = response['query']
    result = response['result']

    # Use the template to render the response
    return template.TemplateResponse("result.html", {"request": {}, "query": query, "rresult": result})

@app.post("/question", response_class=HTMLResponse)
async def load_question_page(request: Request):
    return template.TemplateResponse("question.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...)):
    res = query_users(username)
    if res == 200:
        return template.TemplateResponse("question.html", {"request": {}})
    else:
        return template.TemplateResponse("notfound.html", {"request": {}})

@app.get("/", response_class=HTMLResponse)
async def load_root(request: Request):
    return template.TemplateResponse("login.html", {"request": request})

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 80))
    uvicorn.run(app, host=host, port=port)
