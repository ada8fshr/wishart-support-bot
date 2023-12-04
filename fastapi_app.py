import asyncio
import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone
import logging
import os
import pinecone
from typing import Awaitable

from src.models.chat import ChatHistory, ChatMessage
from src.chat import inference


dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV"),
)
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pinecone.Index(index_name)

openai_api_key = os.getenv("OPENAI_API_KEY")
temperature = os.getenv("TEMPERATURE")
model = os.getenv("MODEL")

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = Pinecone(index, embeddings, "text")
retriever = vectorstore.as_retriever()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/chat")
async def chat(chat_message: ChatMessage, chat_history: ChatHistory):
    
    response = inference(
        message=chat_message.message,
        history=chat_history.history,
        model=model,
        temperature=temperature,
        openai_api_key=openai_api_key,
        retriever=retriever
    )

    logger.info(response)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)