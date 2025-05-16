import json
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from transformers import pipeline
from typing import List, Dict, Any


app = FastAPI()

# Load disease list from file once at startup
with open("diseases.json", "r", encoding="utf-8") as f:
    COMMON_DISEASES = json.load(f)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

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


# Load JSON data at startup
with open("disease_dosage_rules_full.json", "r") as f:
    disease_data: List[Dict[str, Any]] = json.load(f)

def get_dosage_by_age(age: int, rules: List[Dict[str, str]]) -> str:
    for rule in rules:
        age_range = rule["age_range"]
        if "+" in age_range:
            min_age = int(age_range.replace("+", ""))
            if age >= min_age:
                return rule["dosage"]
        else:
            min_age, max_age = map(int, age_range.split("-"))
            if min_age <= age <= max_age:
                return rule["dosage"]
    return "No dosage rule found"

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

@app.get("/medication")
def get_medication(icd: str = Query(...), age: int = Query(...)):
    for disease in disease_data:
        if disease["icd"].lower() == icd.lower():
            result = []
            for med in disease["medications"]:
                dosage = get_dosage_by_age(age, med["age_dosage_rules"])
                result.append({
                    "medication": med["name"],
                    "recommended_dosage": dosage
                })
            return {"disease": disease["disease"], "medications": result}
    return {"error": "ICD code not found"}