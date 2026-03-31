import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")
try:
    response = model.generate_content("Ping", request_options={"timeout": 10})
    print(f"Result: {response.text}")
except Exception as e:
    print(f"Error: {e}")
