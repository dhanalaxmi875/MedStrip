import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from PIL import Image

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Tried in order; if one is overloaded or unavailable we move to the next
MODELS = ["gemini-3.8-flash", "gemini-flash-latest"]

def ask(image, prompt, retries=3):
    for model in MODELS:
        for attempt in range(retries):
            try:
                resp = client.models.generate_content(
                    model=model, contents=[image, prompt]
                )
                print(f"[used model: {model}]")
                return resp.text
            except errors.ServerError:           # 5xx: overloaded, retry
                wait = 2 ** attempt
                print(f"{model}: server busy, retrying in {wait}s...")
                time.sleep(wait)
            except errors.ClientError as e:      # 4xx: bad model name etc.
                print(f"{model}: {e.code} {str(e.message)[:80]}")
                break                            # skip to next model
    raise RuntimeError("All models failed. Try again in a few minutes.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "samples/strip1.jpg"
    img = Image.open(path)
    print(ask(img, "List every piece of text you can read on this medicine strip."))