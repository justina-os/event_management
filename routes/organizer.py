from fastapi import APIRouter,Depends,HTTPException
from routes.loginPage import give_access
from db import get_connection
from pydantic import BaseModel
from datetime import date
from typing import Literal

organizer=APIRouter()

