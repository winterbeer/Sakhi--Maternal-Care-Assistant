from fastapi import FastAPI
from pydantic import BaseModel
from .nutrition_rag2 import query_nutrition_advice

app = FastAPI(title="Sakhi Nutrition API")


class NutritionInput(BaseModel):
    user_id: str
    query: str
    trimester: str | None = None
    language: str = "English"
    diet_type: str | None = None
    budget: str | None = None
    food_notes: str | None = None


@app.get("/")
def root():
    return {"message": "Sakhi Nutrition API is running"}


@app.post("/nutrition-query")
async def query_nutrition_route(input: NutritionInput):

    result = query_nutrition_advice(
        user_id=input.user_id,
        query=input.query,
        trimester=input.trimester,
        language=input.language,
        diet_type=input.diet_type,
        budget=input.budget,
        food_notes=input.food_notes
    )

    return {"result": result}