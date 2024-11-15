from typing import Optional
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import os

USERNAME = os.getenv('FLIGHTHELP24USER', 'default_value')
PASSWORD = os.getenv('FLIGHTHELP24PASS', 'default_value')

security = HTTPBasic()

app = FastAPI()


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    global USERNAME
    global PASSWORD
    current_username = credentials.username
    is_correct_username = current_username == USERNAME
    current_password = credentials.password
    is_correct_password = current_password == PASSWORD
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/items_new/{item_id}")
def read_item_new(username :Annotated[str, Depends(get_current_username)],item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}