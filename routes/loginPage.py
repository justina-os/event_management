from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from auth import hash_password,verify_password
from db import get_connection
from datetime import datetime,timedelta
from jose import JWTError,jwt
from fastapi.security import OAuth2PasswordBearer
from typing import Literal


login_page=APIRouter()




class LoginDetails(BaseModel):
    email: str
    password: str


class SignupDetails(BaseModel):
    name: str
    email: str
    password: str
    role: Literal["organizer", "attendee"]

# SignIn or login

import os

SECRET_KEY = os.getenv("SECRET_KEY")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

oauth_scheme=OAuth2PasswordBearer(tokenUrl="login")

@login_page.post("/login")
def login(detail:LoginDetails):
    con=get_connection()
    cur=con.cursor(dictionary=True)
    
    try:
        cur.execute("select user_id,password from users where email=%s",(detail.email,))
        row = cur.fetchone()
        if row:
            if verify_password(detail.password,row["password"]):
                access_token=create_token({"sub":str(row["user_id"])})
                return{ "access_token": access_token, "token_type": "bearer" }
            else:
                raise HTTPException(status_code=401,detail="Invalid credentials ")
            
        else:
            raise HTTPException(status_code=401,detail="Invalid credentials ")
    finally:
        cur.close()
        con.close()

@login_page.post("/signin")
def sigin(details:SignupDetails):
    con=get_connection()
    cur=con.cursor(dictionary=True)
    
    try:
        cur.execute("select user_id,password from users where email=%s",(details.email,))
        row = cur.fetchone()
        password=hash_password(details.password)
        if not row:
            cur.execute(
    """
    INSERT INTO users (name, email, password, role)
    VALUES (%s, %s, %s, %s)
    """,
    (
        details.name,
        details.email,
        password,
        details.role
    )
)
            con.commit()

            return "Added successfully"
        
        else:
            return "mail_id alredy exsist try again"
    finally:
        cur.close()
        con.close()


def give_access(token:str =Depends(oauth_scheme)):
    
    
    try :
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload["sub"]

        return int(user_id)
    except JWTError:
       raise HTTPException(status_code=401,detail="Invalid or expired token")