import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001/predict"

st.set_page_config(page_title="Titanic Survival Predictor")

st.title("Titanic Survival Prediction")
st.write("Enter passenger details below.")

# Input fields
passenger = st.number_input("Passenger ID", min_value=1, value=1)
pclass = st.selectbox("Passenger Class", [1, 2, 3])
name = st.text_input("Passenger Name")
sex = st.selectbox("Gender", ["male", "female"])
age = st.number_input("Age", min_value=0.0, max_value=100.0, value=25.0)
sibsp = st.number_input("Siblings/Spouses", min_value=0, value=0)
parch = st.number_input("Parents/Children", min_value=0, value=0)
ticket = st.text_input("Ticket Number")
fare = st.number_input("Fare", min_value=0.0, value=7.25)
cabin = st.text_input("Cabin")
embarked = st.selectbox("Embarked", ["S", "C", "Q"])

if st.button("Predict"):

    data = {
        "Passenger": passenger,
        "Survived": None,
        "Pclass": pclass,
        "Name": name,
        "Sex": sex,
        "Age": age,
        "SibSp": sibsp,
        "Parch": parch,
        "Ticket": ticket,
        "Fare": fare,
        "Cabin": cabin,
        "Embarked": embarked
    }

    try:
        response = requests.post(
            API_URL,
            json=data
        )

        if response.status_code == 200:
            result = response.json()

            st.success("Prediction Successful!")

            st.write("### Result")
            st.write(f"Prediction: **{result['prediction']}**")
            st.write(f"Status: **{result['result']}**")

        else:
            st.error(response.text)

    except Exception:
        st.error("Could not connect to the FastAPI server.")