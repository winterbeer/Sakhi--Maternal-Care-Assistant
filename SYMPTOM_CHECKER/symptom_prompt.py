from langchain_core.prompts import PromptTemplate
from langchain_classic.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_community.llms import Ollama

from SHARED.memory_store import (
    get_user_memory,
    update_user_memory,
    add_symptom_entry
)


diagnosis_schema = ResponseSchema(
    name="diagnosis",
    description="Possible explanation of the symptoms in pregnancy context"
)

advice_schema = ResponseSchema(
    name="advice",
    description="Simple, warm, practical advice"
)

is_critical_schema = ResponseSchema(
    name="is_critical",
    description="true if urgent medical attention may be needed, otherwise false"
)

next_steps_schema = ResponseSchema(
    name="next_steps",
    description="Recommended next step"
)

response_schemas = [
    diagnosis_schema,
    advice_schema,
    is_critical_schema,
    next_steps_schema
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

prompt = PromptTemplate(
    template="""
You are a kind and caring maternal health companion.

Talk like a friendly next-door neighbor or elder sister.
Use simple, warm, easy-to-understand language.
Avoid medical jargon.

Reply in this language: {language}
If language is Hinglish, write Hindi in English letters.

User memory:
- Previous trimester: {memory_trimester}
- Recent symptom history: {recent_symptoms}

Current input:
Symptoms: {symptoms}
Severity (1-5): {severity}
Trimester: {trimester}

IMPORTANT:
Return only valid JSON.
Do not write anything before or after the JSON.
Do not use markdown.
Do not use triple backticks.

{format_instructions}
""",
    input_variables=[
        "language",
        "memory_trimester",
        "recent_symptoms",
        "symptoms",
        "severity",
        "trimester"
    ],
    partial_variables={"format_instructions": format_instructions}
)

llm = Ollama(model="llama3")


def analyze_symptom(
    user_id: str,
    symptoms: str,
    severity: int,
    trimester: str,
    language: str = "English"
):
    memory = get_user_memory(user_id)

    recent_symptoms = memory["symptom_history"][-3:] if memory["symptom_history"] else []

    final_prompt = prompt.format(
        language=language,
        memory_trimester=memory.get("trimester"),
        recent_symptoms=recent_symptoms,
        symptoms=symptoms,
        severity=severity,
        trimester=trimester
    )

    raw_output = llm.invoke(final_prompt)
    print("RAW MODEL OUTPUT:\n", raw_output)

    try:
        parsed_output = output_parser.parse(raw_output)
    except Exception:
        parsed_output = {
            "diagnosis": "Could not parse structured response",
            "advice": raw_output,
            "is_critical": False,
            "next_steps": "Please review the model output manually."
        }

    update_user_memory(user_id, {
        "language": language,
        "trimester": trimester
    })

    add_symptom_entry(user_id, {
        "symptoms": symptoms,
        "severity": severity,
        "trimester": trimester,
        "language": language,
        "result_summary": parsed_output.get("diagnosis")
    })

    return parsed_output