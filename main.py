from typing import Optional
from typing import Annotated
import os
from fastapi import Depends, FastAPI, HTTPException, status,Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from crawler import Flightera
import logging

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

@app.get("/flight/{flight_code}")
def read_item(flight_code: str,username :Annotated[str, Depends(get_current_username)]):
    try:
        logging.info(f'Acess flight {flight_code}')
        flight = Flightera()
        return flight.get_flight(flight_code)
    except:
        logging.error(ex)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight dont exsit",
        )


@app.get("/flight_month")
def read_item_new(username :Annotated[str, Depends(get_current_username)],
                  flight_code: str,
                  month_number: int = Query(1,description="Number of the month. Janury = 1, and so on"),
                  year: int = 2023):
    """
    Get details of the flight in the specific month and year
    """
    try:
        logging.info(f'Acess flight {flight_code}')
        flight = Flightera()
        response = flight.get_history_by_date(flight_code,month_number,year)
        return response
    except Exception as ex:
        logging.error(ex)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ex)
        )