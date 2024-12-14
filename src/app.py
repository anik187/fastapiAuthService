from fastapi.requests import Request

from fastapi import FastAPI, HTTPException
from routes.userRoutes import router

app = FastAPI(docs_url=None, redoc_url=None)
app.include_router(router)


@app.get("/", status_code=200)
def home(request: Request):
    if "accessToken" not in request.cookies:
        raise HTTPException(status_code=401, detail="Not Authorized!!")

    return "you are most welcome!!!"
