import sys
from google.genai import types
from PIL import Image
from gemini_client import ask
from schema import ScanResult

PROMPT = """You are reading a photo of medicine packaging.
Extract ONLY text that is physically printed on the packaging and clearly legible.

Rules:
1. Never guess or complete text that is covered, cut off, blurry or hidden by glare. Set that field to null and describe what you could not read in unreadable_parts.
2. Do not use outside knowledge to fill any field. Record only what the pack says.
3. If the same medicine is printed more than once (repeated sections), return it once.
4. Ignore website overlays, watermarks and tags added on top of the photo. They are not printed on the packaging.
5. Return one entry per distinct medicine in the photo.
6. If something is listed in unreadable_parts, do NOT also transcribe it in any other field. Unreadable means null, not a best guess.
"""

def scan_medicines(image):
    config = types.GenerateContentConfig(
        response_mime_type="application/json",   # reply must be JSON
        response_schema=ScanResult,              # ...in this exact shape
        temperature=0,                           # least random, most repeatable
    )
    resp = ask(image, PROMPT, config=config)
    return resp.parsed                           # a ScanResult object, or None

if __name__ == "__main__":
    result = scan_medicines(Image.open(sys.argv[1]))
    if result is None:
        print("Model reply did not match the schema.")
    else:
        print(result.model_dump_json(indent=2))