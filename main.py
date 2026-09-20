import json
from typing import Annotated, Literal,Optional

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[
        str,
        Field(description="ID of the patient", examples=["P001"])
    ]

    name: Annotated[
        str,
        Field(description="Name of the patient", examples=["John Doe"])
    ]

    city: Annotated[
        str,
        Field(description="City of the patient", examples=["Mumbai"])
    ]

    age: Annotated[
        int,
        Field(gt=0, lt=120, description="Age of the patient", examples=[30])
    ]

    gender: Annotated[
        Literal["male", "female", "other"],
        Field(description="Gender of the patient", examples=["male"])
    ]

    height: Annotated[
        float,
        Field(gt=0, description="Height in meters", examples=[1.75])
    ]

    weight: Annotated[
        float,
        Field(gt=0, description="Weight in kg", examples=[70.5])
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal weight"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obesity"

class PatientUpdate(BaseModel):
    name: Annotated[
        Optional[str],
        Field(description="Name of the patient", examples=["John Doe"])
    ] = None

    city: Annotated[
        Optional[str],
        Field(description="City of the patient", examples=["Mumbai"])
    ] = None

    age: Annotated[
        Optional[int],
        Field(gt=0, lt=120, description="Age of the patient", examples=[30])
    ] = None

    gender: Annotated[
        Optional[Literal["male", "female", "other"]],
        Field(description="Gender of the patient", examples=["male"])
    ] = None

    height: Annotated[
        Optional[float],
        Field(gt=0, description="Height in meters", examples=[1.75])
    ] = None

    weight: Annotated[
        Optional[float],
        Field(gt=0, description="Weight in kg", examples=[70.5])
    ] = None


   
def load_data():
    with open("patients.json", "r") as f:
        return json.load(f)


def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)


@app.get("/")
def hello():
    return {"message": "Patient Management System API"}


@app.get("/about")
def about():
    return {
        "message": "A fully functional API to manage your patient records."
    }


@app.get("/view")
def view():
    return load_data()


@app.get("/patient/{patient_id}")
def get_patient(
    patient_id: str = Path(
        ...,
        description="Patient ID",
        examples=["P001"]
    )
):
    data = load_data()

    if patient_id in data:
        return data[patient_id]

    raise HTTPException(
        status_code=404,
        detail=f"Patient with ID {patient_id} not found."
    )


@app.get("/sort")
def sort_patients(
    sort_by: str = Query(
        ...,
        description="Sort by height, weight or bmi"
    ),
    order: str = Query(
        "asc",
        description="Sort order: asc or desc"
    )
):
    valid_fields = ["height", "weight", "bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field. Choose from {valid_fields}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Order must be asc or desc."
        )

    data = load_data()

    patients = []

    for patient in data.values():
        if sort_by == "bmi":
            bmi = round(patient["weight"] / (patient["height"] ** 2), 2)
            patient["bmi"] = bmi
        patients.append(patient)

    sorted_data = sorted(
        patients,
        key=lambda x: x[sort_by],
        reverse=(order == "desc")
    )

    return sorted_data


@app.post("/create", status_code=201)
def create_patient(patient: Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(
            status_code=400,
            detail=f"Patient with ID {patient.id} already exists."
        )

    data[patient.id] = patient.model_dump(exclude={"id"})

    save_data(data)

    return {
        "message": f"Patient with ID {patient.id} created successfully."
    }

@app.put("/update/{patient_id}")
def update_patient(
    patient_id: str,
    patient_update: PatientUpdate
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with ID {patient_id} not found."
        )

    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    existing_patient_info["id"] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_obj.model_dump(exclude={"id"})

    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Patient with ID {patient_id} updated successfully."
        }
    )

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with ID {patient_id} not found."
        )

    del data[patient_id]

    save_data(data)

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Patient with ID {patient_id} deleted successfully."
        }
    )