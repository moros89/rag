from langchain_openai import OpenAIEmbeddings
from load_config import read_json_config

def create_embeddings():
    config = read_json_config("./documents/config.json")

    # config = read_json_config("./documents/remote_config.json")

    embeddings = OpenAIEmbeddings(
        api_key = config["api_key"],
        openai_api_base = config["openai_api_base"],
        model = config["embedding_model"]
    )

    return embeddings

public_embeddings = create_embeddings()