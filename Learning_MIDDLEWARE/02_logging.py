from fastapi import FastAPI, Request
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the request start
    start_time = time.time()
    method = request.method
    url = request.url
    
    logger.info(f"Starting {method} request to {url}")
    
    # Process the request
    response = await call_next(request)
    
    # Log the request completion
    process_time = time.time() - start_time
    logger.info(f"Completed {method} request to {url} in {process_time:.4f}s")
    
    return response


"""
The decorator `@app.middleware("http")` specifies that the function it decorates will act as an **HTTP middleware** . This means the function will intercept every HTTP request and response that passes through the FastAPI application.
"""

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}