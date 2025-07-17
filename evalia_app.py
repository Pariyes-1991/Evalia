from fastapi import FastAPI, UploadFile, File
import pandas as pd
from transformers import pipeline
from typing import List
import uvicorn

app = FastAPI()

# Load AI pipeline for sentiment analysis
try:
    pipe = pipeline("sentiment-analysis", model="distilroberta-base-sst-2")
except Exception as e:
    print(f"Error loading pipeline: {e}. Using rule-based logic.")
    pipe = None

def analyze_applicant(row):
    try:
        height_m = float(row.get('Height_cm', 0)) / 100
        weight = float(row.get('Weight_kg', 0))
        bmi = weight / (height_m ** 2) if height_m > 0 else 0
        
        position = str(row.get('Position', '')).lower()
        experience_years = float(row.get('Experience_Years', 0))
        input_text = f"Position: {position}, Experience: {experience_years} years"
        
        level = "Mid"
        reason = "Analysis based on rule-based logic"
        
        if pipe:
            result = pipe(input_text)[0]
            sentiment = result['label']
            score = result['score']
            if sentiment == "POSITIVE" and experience_years >= 2:
                level = "High"
            elif sentiment == "NEGATIVE" or bmi > 25:
                level = "Low"
            else:
                level = "Mid"
            reason = f"AI sentiment: {sentiment} (score: {score:.2f}, experience: {experience_years} years)"
        
        if bmi > 25:
            level = "Low"
            reason = "BMI exceeds 25, indicating potential health concerns"
        elif not pipe:
            if 'senior' in position or experience_years >= 5:
                level = "High"
            elif experience_years >= 2:
                level = "Mid"
            else:
                level = "Low"
            reason = "Rule-based analysis due to pipeline failure"
        
        return {"BMI": round(bmi, 1), "Level": level, "Reason": reason}
    except Exception as e:
        return {"BMI": 0, "Level": "Low", "Reason": f"Error in analysis: {str(e)}"}

@app.post("/analyze")
async def analyze_excel(file: UploadFile = File(...)):
    try:
        df = pd.read_excel(file.file)
        results = df.apply(analyze_applicant, axis=1).to_dict()
        df = pd.concat([df, pd.DataFrame(results).T], axis=1)
        return {"status": "success", "data": df.to_dict(orient="records")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
