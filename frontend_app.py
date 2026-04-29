import streamlit as st
import requests
import pyttsx3

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Sakhi MVP", page_icon="🌸", layout="centered")

st.title("🌸 Sakhi Maternal Care Assistant")
st.write("A simple multilingual maternal care assistant for symptom and nutrition support.")

user_id = st.text_input("User ID", value="test_001")
language = st.selectbox("Language", ["English", "Hindi", "Hinglish"])

module = st.sidebar.radio(
    "Choose Module",
    ["Symptom Checker", "Nutrition Advisor"]
)


def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


if module == "Symptom Checker":
    st.header("🩺 Symptom Checker")

    symptoms = st.text_area("Describe your symptoms")
    severity = st.slider("Severity", 1, 5, 2)
    trimester = st.selectbox("Trimester", ["first", "second", "third"])

    if st.button("Check Symptoms"):
        payload = {
            "user_id": user_id,
            "symptoms": symptoms,
            "severity": severity,
            "trimester": trimester,
            "language": language
        }

        response = requests.post(
            f"{BACKEND_URL}/symptom/analyze-symptom",
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            result = data.get("response") or data.get("result") or data
            st.success("Response received")

            st.write("### Diagnosis")
            st.write(result.get("diagnosis"))

            st.write("### Advice")
            st.write(result.get("advice"))

            st.write("### Critical?")
            st.write(result.get("is_critical"))

            st.write("### Next Steps")
            st.write(result.get("next_steps"))

            if st.button("🔊 Speak Advice"):
                speak_text(result.get("advice", ""))
        else:
            st.error(response.text)


if module == "Nutrition Advisor":
    st.header("🥗 Nutrition Advisor")

    query = st.text_area("Ask your nutrition question")
    trimester = st.selectbox("Trimester", ["first", "second", "third"])
    diet_type = st.selectbox("Diet Type", ["vegetarian", "non-vegetarian", "mixed"])
    budget = st.selectbox("Budget", ["low", "medium", "high"])
    food_notes = st.text_input("Food notes / symptoms", value="")

    if st.button("Get Nutrition Advice"):
        payload = {
            "user_id": user_id,
            "query": query,
            "trimester": trimester,
            "language": language,
            "diet_type": diet_type,
            "budget": budget,
            "food_notes": food_notes
        }

        response = requests.post(
            f"{BACKEND_URL}/nutrition/nutrition-query",
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            result = data.get("response") or data.get("result") or data

            st.success("Response received")

            st.write("### Answer")
            st.write(result.get("answer"))

            st.write("### Sources Used")
            for source in result.get("sources_used", []):
                st.write(f"**Document:** {source.get('document_name')}")
                st.write(f"**Page:** {source.get('page_number')}")
                st.write(source.get("snippet"))
                st.divider()

            if st.button("🔊 Speak Answer"):
                speak_text(result.get("answer", ""))
        else:
            st.error(response.text)