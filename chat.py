from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Set up LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"
llm = OpenAI(api_key=OPENAI_API_KEY)

# Basic Chat

completion = llm.chat.completions.create(
    model = MODEL,
    messages=[
        {"role":"system", "content":"You are a helpful assistant. Help me with my math homework"},
        {"role":"user", "content":"Hello! I have a right anlged triangle with sides of length 7, 24 and 25. Alpha is the smallest internal angle. What is the sin of alpha?"}
    ]
)

print(f"Assistant: {completion.choices[0].message.content}")