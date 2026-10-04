from typing import Literal, Optional
from pydantic import BaseModel, Field

class Medicine(BaseModel):
    brand_name: Optional[str] = Field(description="Brand name exactly as printed")
    generic_name: Optional[str] = Field(description="Generic name as printed")
    active_ingredients: list[str] = Field(
        description='Each active ingredient with strength as printed, e.g. "Paracetamol IP 500 mg"')
    form: Optional[str] = Field(description="tablet, capsule, syrup, etc., if printed")
    printed_strength: Optional[str] = Field(
    description='Strength printed next to the brand name, e.g. "4 mg", if any')
    manufacturer: Optional[str]
    printed_dosage_text: Optional[str] = Field(
        description="Dosage instructions exactly as printed, or null")
    printed_warnings: list[str]
    legibility: Literal["clear", "partial", "poor"]
    unreadable_parts: list[str] = Field(
        description="Parts of this pack that are covered, cut off, blurry or glare-obscured")

class ScanResult(BaseModel):
    medicines: list[Medicine]
    image_quality: Literal["good", "fair", "poor"]
    notes: Optional[str]