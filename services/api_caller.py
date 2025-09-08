import httpx
from fastapi import HTTPException

async def call_iap_api(url: str, payload: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
