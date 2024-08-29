from fastapi import FastAPI
from pydantic import BaseModel
from rag import read_json_config, load_and_split_documents, create_vector_store, setup_rag_chain, ask_question
import uvicorn

app = FastAPI()

class Request(BaseModel):
    question: str

class Public:
    def __init__(self) -> None:
        # step 1: load config
        config = read_json_config("./documents/config.json")

        # step 2: load documents and pre operations
        self.docs = load_and_split_documents()

        # step 3: creating vectorDB
        self.vector_store = create_vector_store(config, self.docs)

        # step 4: creating the index and the chain
        self.chain = setup_rag_chain(config, self.vector_store)

public = Public()

@app.get("/query/")
async def query(request: Request):
    response = ask_question(public.chain, request.question)

    return {"response": response.result}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port, reload=True)
