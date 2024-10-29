from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.api.login_register import router as login_router
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from app.api.images import router as images
from app.api.products import router as prods
from app.api.basket import router as basket

import uvicorn
app = FastAPI()

origins = [
    "http://localhost:5173", 
]

templates = Jinja2Templates(directory='templates')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Barcha domenlardan ruxsat berish
    allow_credentials=True,
    allow_methods=["*"],  # Barcha metodlar (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Barcha headerlar
)

@app.get("/")
async def read_root(request: Request):
    # URL ni olish
    url = f"{request.url.scheme}://{request.url.netloc}"
    return {"message": "Hello World", "url": url}
app.include_router(login_router)
app.include_router(images)
app.include_router(prods)
app.include_router(basket)
if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='192.168.1.15')