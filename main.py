

import uvicorn

if __name__=="__main__":
    uvicorn.run('product.main:app', reload=True)