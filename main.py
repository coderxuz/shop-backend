from fastapi import FastAPI, Request
from app.api.login_register import router as login_router
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.images import router as images
from app.api.products import router as prods
from app.api.basket import router as basket
from app.api.order import router as order

import uvicorn

app = FastAPI()

origins = ["http://localhost:5173", "http://192.168.1.15:5173"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root(request: Request):
    template = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        body{{
            color: #fff;
            background-color: #000;
        }}
        a{{
            color: #fff;
        }}
    </style>
</head>
<body>
    <h1>Web server</h1>
    <a href="{a}://{b}/docs" target='_blank'>docs</a>

</body>
</html>
    """.format(a=request.url.scheme,b=request.url.netloc)
    return HTMLResponse(content=template)


app.include_router(login_router)
app.include_router(images)
app.include_router(prods)
app.include_router(basket)
app.include_router(order)
if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="192.168.1.15")
