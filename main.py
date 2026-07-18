from fastapi import FastAPI
from routes.loginPage import login_page as login 
from routes.create_events import create as create
from routes.attende import attende as attende
from routes.organizer import organizer as org
app=FastAPI()

app.include_router(login)
app.include_router(create)
app.include_router(org)
app.include_router(attende)

