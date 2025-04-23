from fastapi import FastAPI, Depends, HTTPException, Request, Header
from typing import Optional

app = FastAPI()

async def verify_token(x_token: Optional[str] = Header(None)):
    """This function acts like middleware but is a dependency"""
    if not x_token:
        raise HTTPException(status_code=400, detail="X-Token header missing")
    if x_token != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid X-Token")
    # We can return data that will be passed to the endpoint
    return {"token_data": "some_user_id"}

async def log_request(request: Request):
    """This dependency logs request information"""
    print(f"Request to {request.url.path}")
    # This doesn't return anything, just performs an action

@app.get("/items/", dependencies=[Depends(log_request)])
async def read_items(token_data: dict = Depends(verify_token)):
    # token_data contains what verify_token returns
    return {"token_data": token_data, "items": ["Item1", "Item2"]}

@app.get("/status/")
async def get_status():
    # This endpoint doesn't use the verify_token dependency
    return {"status": "ok"}

@app.get("/")
async def index():
    # This endpoint doesn't use the verify_token dependency
    return {"goto": "/items"}