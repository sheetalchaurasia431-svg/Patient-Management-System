from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated, Optional
import pickle
import pandas as pd

# ==========================
# Load Machine Learning Model
# ==========================
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

print("Titanic app is running")


app = FastAPI(
    title="Titanic Survival Prediction API",
    description="Predict whether a Titanic passenger would survive using a Machine Learning model.",
    version="1.0.0"
)


class UserInput(BaseModel):

    Passenger: Annotated[
        int,
        Field(..., gt=0, description="Passenger ID", examples=[1])
    ]

    Survived: Annotated[
        Optional[int],
        Field(None, ge=0, le=1, description="Leave blank for prediction")
    ]

    Pclass: Annotated[
        int,
        Field(..., ge=1, le=3, description="Passenger Class", examples=[3])
    ]

    Name: Annotated[
        str,
        Field(..., description="Passenger Name", examples=["John Doe"])
    ]

    Sex: Annotated[
        str,
        Field(..., description="Gender", examples=["male"])
    ]

    Age: Annotated[
        float,
        Field(..., gt=0, lt=100, description="Age", examples=[25])
    ]

    SibSp: Annotated[
        int,
        Field(..., ge=0, description="Number of Siblings/Spouses", examples=[1])
    ]

    Parch: Annotated[
        int,
        Field(..., ge=0, description="Number of Parents/Children", examples=[0])
    ]

    Ticket: Annotated[
        str,
        Field(..., description="Ticket Number", examples=["A/5 21171"])
    ]

    Fare: Annotated[
        float,
        Field(..., ge=0, description="Passenger Fare", examples=[7.25])
    ]

    Cabin: Annotated[
        Optional[str],
        Field(None, description="Cabin Number", examples=["C85"])
    ]

    Embarked: Annotated[
        Optional[str],
        Field(None, description="Embarked Port", examples=["S"])
    ]


# ==========================
# Home Endpoint
# ==========================
@app.get("/")
def home():
    return {
        "message": "Welcome to Titanic Survival Prediction API 🚢"
    }


# ==========================
# Prediction Endpoint
# ==========================
@app.post("/predict")
def predict(data: UserInput):

    try:

        # Convert request to dictionary
        input_data = data.model_dump()

        # Convert dictionary to DataFrame
        df = pd.DataFrame([input_data])

        # Make prediction
        prediction = model.predict(df)[0]

        # Convert prediction to readable text
        if prediction == 1:
            result = "Survived"
        else:
            result = "Did Not Survive"

        return {

            "status": "Success",

            "prediction": int(prediction),

            "result": result,

            "passenger_details": {

                "Passenger Class": data.Pclass,
                "Gender": data.Sex,
                "Age": data.Age,
                "Fare": data.Fare,
                "Embarked": data.Embarked

            }

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )