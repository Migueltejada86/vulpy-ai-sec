import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)

def llm_call(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content
