from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# In a real application, you would store tokens more securely
VALID_API_KEYS = ["secret_key_1", "secret_key_2"]

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    # Exclude authentication for specific paths
    if request.url.path == "/docs" or request.url.path == "/redoc" or request.url.path == "/openapi.json":
        return await call_next(request)
    
    # Check for API key in header
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in VALID_API_KEYS:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key"}
        )
    
    # If authenticated, proceed with the request
    response = await call_next(request)
    return response

@app.get("/protected")
async def protected_route():
    return {"message": "This is a protected route"}

@app.get("/public")
async def public_route():
    # Even though we named this "public", our middleware will still require authentication
    # since it applies to all routes
    return {"message": "This is a public route"}