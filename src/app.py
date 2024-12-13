import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from routes.userRoutes import router

app = FastAPI()
app.include_router(router)


@app.get("/")
def home(request: Request):
    if "accessToken" not in request.cookies:
        raise HTTPException(status_code=401, detail="Not Authorized!!")

    return "hello world"


if __name__ == "__main__":
    uvicorn.run(app="app:app", host="0.0.0.0", reload=True, port=8000)
