import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key= os.getenv('API_KEY'))

response = client.responses.create(
    model="gpt-6-luna",
    input="Write a one-sentence about Sri Lanka.",
)

print(response.output_text)