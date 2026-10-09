import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load variables from .env
load_dotenv()

# Get the API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")

# Create Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash",
    google_api_key=api_key,
    temperature=0
)

# Send a test question
response = llm.invoke(
    "You are KartEase customer support. Say hello and briefly introduce yourself."
)

print("\nGemini response:")
print(response.content)