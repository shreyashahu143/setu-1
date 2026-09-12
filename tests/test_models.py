# First, install the new library: pip install google-genai
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

# Ensure your GOOGLE_API_KEY is set in your environment variables
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

print("Available Gemini Models:")
for model in client.models.list():
    print(f"- {model.name}")
