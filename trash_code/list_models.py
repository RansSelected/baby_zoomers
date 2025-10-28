from google import genai
import os

print("Attempting to list models...")

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    print("Available models that support generateContent:")
    for model in client.models.list():
      if 'generateContent' in model.supported_actions:
        print(model.name)

except ImportError:
    print("ERROR: The 'google-genai' library is not installed correctly.")
    print("Please make sure it is installed in your environment.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    