import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from fastapi.responses import JSONResponse

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]
devices.create_index("name", unique=True)

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


@app.post("/devices", status_code=201)
def create_device(device: Device):
    new_device = device.model_dump()
    try:
        devices.insert_one(new_device.copy())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="A device called " + device.name + " already exists"
        )
    return JSONResponse(
        status_code=201,
        content=new_device,
        headers={"Location": "/devices/" + device.name}
    )



@app.put("/devices/{name}")
def put_device(name: str, device: Device):
    if device.name != name:
        raise HTTPException(
            status_code=409,
            detail="Device name must match URL"
        )
    new_device = device.model_dump()
    result = devices.replace_one(
        {"name": name},
        new_device.copy(),
        upsert=True
    )
    if result.upserted_id is not None:
        return JSONResponse(
            status_code=201,
            content=new_device,
            headers={"Location": "/devices/" + name}
        )
    return new_device



@app.delete("/devices/{name}")
def delete_device(name: str):
    result = devices.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(404, "Device not found")
    return {"message": "Device deleted successfully"}
