###
import os
from langchain_groq import ChatGroq

def llm_call(prompt: str) -> str:
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192",
        temperature=0
    )
    return llm.invoke(prompt).content
