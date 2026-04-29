from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama

from SHARED.memory_store import (
    get_user_memory,
    update_user_memory,
    add_nutrition_entry
)

# Load once, not on every request
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory="NUTRITION_ADVISOR/vector_store",
    embedding_function=embedding_model,
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

llm = Ollama(model="llama3")


def build_sources(docs):
    sources = []

    for doc in docs:
        page = doc.metadata.get("page")
        page_number = page + 1 if isinstance(page, int) else "Unknown page"

        sources.append({
            "document_name": doc.metadata.get("source", "Unknown document"),
            "page_number": page_number,
            "snippet": doc.page_content[:500]
        })

    return sources


def query_nutrition_advice(
    user_id: str,
    query: str,
    trimester: str | None = None,
    language: str = "English",
    diet_type: str | None = None,
    budget: str | None = "low",
    food_notes: str | None = None
):
    memory = get_user_memory(user_id)

    preferences = {}
    if diet_type:
        preferences["diet_type"] = diet_type
    if budget:
        preferences["budget"] = budget
    if food_notes:
        preferences["food_notes"] = food_notes

    updates = {"language": language}

    if trimester:
        updates["trimester"] = trimester

    if preferences:
        updates["preferences"] = preferences

    update_user_memory(user_id, updates)
    memory = get_user_memory(user_id)

    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = build_sources(docs)

    recent_symptoms = memory["symptom_history"][-2:] if memory["symptom_history"] else []
    recent_nutrition = memory["nutrition_history"][-2:] if memory["nutrition_history"] else []

    if not docs or len(context.strip()) < 100:
        answer = (
            "Mere PDF documents me iska clear jawab nahi mila."
            if language.lower() in ["hindi", "hinglish"]
            else "I could not find a clear answer in the PDF documents."
        )

        return {
            "answer": answer,
            "sources_used": [],
            "memory_used": {
                "trimester": memory.get("trimester"),
                "recent_symptoms": recent_symptoms,
                "diet_type": memory["preferences"].get("diet_type"),
                "budget": memory["preferences"].get("budget"),
                "food_notes": memory["preferences"].get("food_notes")
            }
        }

    prompt = f"""
You are Sakhi, a maternal nutrition assistant.

You must answer ONLY from the retrieved PDF context below.

STRICT RULES:
- Do not use your own general knowledge.
- Do not add foods, advice, facts, or recommendations that are not present in the PDF context.
- If the PDF context does not contain the answer, say:
  "Mere PDF documents me iska clear jawab nahi mila."
- Keep the answer simple, warm, and rural-friendly.
- Prefer low-cost foods only if they are mentioned in the PDF context.
- Do not suggest expensive foods unless they are clearly present in the PDF context.
- Do not invent document names or page numbers.
- Source document names and page numbers will be shown separately by the system.

Reply in this language: {language}
If language is Hinglish, write Hindi in English letters.

User memory:
- trimester: {memory.get("trimester")}
- recent symptoms: {recent_symptoms}
- diet type: {memory["preferences"].get("diet_type")}
- budget: {memory["preferences"].get("budget")}
- food notes: {memory["preferences"].get("food_notes")}
- recent nutrition questions: {recent_nutrition}

Retrieved PDF context:
{context}

User question:
{query}

Answer only using the retrieved PDF context.
"""

    answer = llm.invoke(prompt)

    add_nutrition_entry(user_id, {
        "query": query,
        "trimester": memory.get("trimester"),
        "language": language,
        "diet_type": memory["preferences"].get("diet_type"),
        "budget": memory["preferences"].get("budget"),
        "food_notes": memory["preferences"].get("food_notes"),
        "sources_used": sources
    })

    return {
        "answer": answer,
        "sources_used": sources,
        "memory_used": {
            "trimester": memory.get("trimester"),
            "recent_symptoms": recent_symptoms,
            "diet_type": memory["preferences"].get("diet_type"),
            "budget": memory["preferences"].get("budget"),
            "food_notes": memory["preferences"].get("food_notes")
        }
    }