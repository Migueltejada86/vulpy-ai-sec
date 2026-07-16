import os
from dotenv import load_dotenv

load_dotenv()
from groq import Groq


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def llm_call(prompt, model="llama-3.3-70b-versatile"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content
