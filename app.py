import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


@app.get("/devices")
def get_all_devices():
    return list(devices.find({}, {"_id": 0}))


@app.get("/devices/{name}")
def get_one_device(name: str):
    device = devices.find_one(
        {"name": name},
        {"_id": 0}
    )
    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )
    return device
