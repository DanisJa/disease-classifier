import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from transformers import pipeline

app = FastAPI()

# Load disease list from file once at startup
with open("diseases.json", "r", encoding="utf-8") as f:
    COMMON_DISEASES = json.load(f)

classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-deberta-v3-small")

class HealthData(BaseModel):
    text: str = Field(..., description="Patient symptoms or description")
    weight: Optional[float] = Field(None, gt=0, description="Weight in kilograms")
    height: Optional[float] = Field(None, gt=0, description="Height in centimeters")
    blood_pressure: Optional[str] = Field(
        None,
        pattern=r"^\d{2,3}\/\d{2,3}$",
        description="Blood pressure as 'systolic/diastolic', e.g. '120/80'"
    )
    temperature: Optional[float] = Field(None, description="Body temperature in Celsius")
    age: Optional[int] = Field(None, gt=0, description="Age in years")
    gender: Optional[str] = Field(
        None,
        pattern="^(male|female|other)$",
        description="Gender: male, female, or other"
    )
    diseases: Optional[List[str]] = Field(None, description="Optional list of diseases to consider")

@app.post("/predict")
def predict(data: HealthData):
    diseases = data.diseases if data.diseases else COMMON_DISEASES

    if len(diseases) > 100:
        raise HTTPException(status_code=400, detail="Disease list too long (max 100 allowed)")

    structured_info_parts = []
    if data.age:
        structured_info_parts.append(f"Age: {data.age}")
    if data.gender:
        structured_info_parts.append(f"Gender: {data.gender}")
    if data.weight:
        structured_info_parts.append(f"Weight: {data.weight} kg")
    if data.height:
        structured_info_parts.append(f"Height: {data.height} cm")
    if data.blood_pressure:
        structured_info_parts.append(f"Blood Pressure: {data.blood_pressure}")
    if data.temperature:
        structured_info_parts.append(f"Temperature: {data.temperature}°C")

    structured_info = ", ".join(structured_info_parts)
    prompt = f"{structured_info}. Symptoms: {data.text}" if structured_info else data.text

    result = classifier(prompt, candidate_labels=diseases)

    return {
        "predicted_disease": result["labels"][0],
        "predictions": [{"disease": label, "score": score} for label, score in zip(result["labels"], result["scores"])]
    }
