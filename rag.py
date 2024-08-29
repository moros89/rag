from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def read_json_config(filename):
    with open(filename, 'r') as f:
        config = json.load(f)
    return config

# Step 1: 加载文档并进行预处理
def load_and_split_documents():
    loader = TextLoader("documents/doc1.txt")
    documents = loader.load()

    loader = TextLoader("documents/doc2.txt")
    documents.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(documents)
    return split_docs

# Step 2: 创建向量数据库
def create_vector_store(config, docs):
    embeddings = OpenAIEmbeddings(
        api_key = config["api_key"],
        openai_api_base = config["openai_api_base"],
        model = config["embedding_model"]
    )
    vector_store = FAISS.from_documents(docs, embeddings)
    return vector_store

# Step 3: 设置检索和生成链
def setup_rag_chain(config, vector_store):
    llm = ChatOpenAI(
        api_key = config["api_key"],
        base_url = config["base_url"]
    )
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
    )
    return rag_chain

# Step 4: 使用 RAG 进行问答
def ask_question(chain, question):
    response = chain.run(question)
    return response