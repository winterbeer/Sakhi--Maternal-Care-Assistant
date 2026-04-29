from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_community.llms import Ollama
from langchain.chains import LLMChain

template = PromptTemplate(
    template= """ You are SAKHI  , a loving next door aunty who cares about pregnant women and their well being. You are friendly, understanding, and skilled in recognizing pregnancy symptoms. You give nutrition advice based on the following details:
    details:
    - Symptoms: {symptoms}
    - Severity of symptoms (scale 1 to 5): {severity}
    - Trimester: {trimester}
    - dietary restrictions: {dietary_restrictions}
    - dietary preferences: {dietary_preferences}
    - knowledge of local food availability: {local_food_availability}
    - cultural considerations: {cultural_considerations}
    - nutritional needs: {nutritional_needs}
    - lifestyle factors: {lifestyle_factors}
    
    Please provide:
    1. A full-day **diet plan**: breakfast, lunch, snack, and dinner with simple Indian food suggestions (prefer local/rural ingredients).
    2. An **explanation** for why these foods are suggested.
    3. Important **warnings** (foods to avoid or limit).
    4. **Hydration tips**
    


    {format_instructions}

    
    
    """,

    input_variables=["symptoms", "severity", "trimester", "dietary_restrictions", "dietary_preferences",
                     "local_food_availability", "cultural_considerations", "nutritional_needs", "lifestyle_factors", "format_instructions"],
)



# Response schema for structured output
response_schemas = [
    ResponseSchema(
        name="diet_plan",
        description="A full-day diet plan including breakfast, lunch, snack, and dinner with simple Indian food suggestions"
    ),
    ResponseSchema(
        name="explanation",
        description="Explanation for why these foods are suggested"
    ),
    ResponseSchema(
        name="warnings",
        description="Important warnings about foods to avoid or limit"
    ),
    ResponseSchema(
        name="hydration_tips",
        description="Hydration tips for the pregnant women"
    )]


parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = parser.get_format_instructions()

# Initialize the Ollama LLM with llama3 model (make sure you have it running locally)
llm = Ollama(model="llama3")

# Create the LangChain chain with your prompt and parser
chain = template | llm | parser

result = chain.invoke({
    "severity": "moderate",
    "symptoms": "nausea, vomiting",
    "trimester": "second",
    "dietary_restrictions": "none",
    "dietary_preferences": "vegetarian",
    "local_food_availability": "available",
    "cultural_considerations": "Indian cuisine",
    "nutritional_needs": "high protein, iron-rich foods",
    "lifestyle_factors": "active lifestyle, moderate exercise",
    "format_instructions": format_instructions

})

print(result)
