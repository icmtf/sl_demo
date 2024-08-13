from fastapi import FastAPI, Query
from typing import List, Optional, Dict
import json

app = FastAPI()

# Load data
with open('data.json', 'r') as f:
    devices = json.load(f)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/devices")
async def get_devices(
    filters: Optional[str] = Query(None, description="Filters in JSON format")
):
    filtered_devices = devices

    if filters:
        try:
            filters_dict = json.loads(filters)
            for key, value in filters_dict.items():
                filtered_devices = [d for d in filtered_devices if str(d.get(key)).lower() == str(value).lower()]
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format for filters"}

    return filtered_devices

@app.get("/keys_and_values")
async def get_keys_and_values():
    keys_and_values = {}
    for device in devices:
        for key, value in device.items():
            if key not in keys_and_values:
                keys_and_values[key] = set()
            keys_and_values[key].add(str(value))
    
    return {k: list(v) for k, v in keys_and_values.items()}