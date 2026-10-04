import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = ["gemini-3.8-flash", "gemini-flash-latest"]

def ask(image, prompt, config=None, retries=3):
    for model in MODELS:
        for attempt in range(retries):
            try:
                resp = client.models.generate_content(
                    model=model, contents=[image, prompt], config=config
                )
                print(f"[used model: {model}]")
                return resp                      # whole response, not just text
            except errors.ServerError:
                wait = 2 ** attempt
                print(f"{model}: server busy, retrying in {wait}s...")
                time.sleep(wait)
            except errors.ClientError as e:
                print(f"{model}: {e.code} {str(e.message)[:80]}")
                break
    raise RuntimeError("All models failed. Check the messages above.")