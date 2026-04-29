from fastapi import FastAPI
from SYMPTOM_CHECKER.main import app as symptom_app
from NUTRITION_ADVISOR.main import app as nutrition_app

app = FastAPI(title="Sakhi Maternal Care Assistant MVP")


@app.get("/")
def home():
    return {
        "message": "Sakhi MVP backend is running",
        "modules": ["Symptom Checker", "Nutrition Advisor"]
    }


app.mount("/symptom", symptom_app)
app.mount("/nutrition", nutrition_app)