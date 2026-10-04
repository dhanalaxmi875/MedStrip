import re
import sys
from PIL import Image
from extractor import scan_medicines
from schema import Medicine

# number + unit, e.g. "500 mg", "2.5 mg", "5 ml", "100 IU"
STRENGTH = re.compile(r"\d+(\.\d+)?\s*(mg|mcg|µg|g|ml|iu|%)", re.IGNORECASE)

def triage(med: Medicine, image_quality: str) -> dict:
    name = med.brand_name or med.generic_name

    # No name or a bad photo: nothing else can be trusted
    if image_quality == "poor" or not name:
        return {"name": name, "status": "retake",
                "reasons": ["Could not read a medicine name. Please retake the photo."],
                "unreadable_parts": med.unreadable_parts}

    reasons = []
    if not med.active_ingredients:
        reasons.append("No active ingredient was readable on the pack.")
    else:
        for ing in med.active_ingredients:
            if not STRENGTH.search(ing):
                reasons.append(f'No strength found for "{ing}".')

    if med.legibility == "poor":
        reasons.append("Pack legibility is poor.")

    status = "confirm" if reasons else "ok"
    return {"name": name, "status": status, "reasons": reasons,
            "unreadable_parts": med.unreadable_parts}

if __name__ == "__main__":
    result = scan_medicines(Image.open(sys.argv[1]))
    if result is None:
        print("Scan failed: reply did not match the schema.")
        sys.exit(1)
    for med in result.medicines:
        t = triage(med, result.image_quality)
        print(f"\n{t['name']}: {t['status'].upper()}")
        for r in t["reasons"]:
            print("  -", r)
        for u in t["unreadable_parts"]:
            print("  (unreadable)", u)