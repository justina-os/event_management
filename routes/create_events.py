from fastapi import APIRouter,Depends,HTTPException
from routes.loginPage import give_access
from db import get_connection
from pydantic import BaseModel
from datetime import date
from typing import Literal

create=APIRouter()

class CreateEvent(BaseModel):
    event_name:str
    event_description :str
    venue:str
    capacity:int
    event_date:date
    registration_deadline:date
    event_status:Literal['draft','published','cancelled','completed']
    

class UpdateEvent(BaseModel):
    event_name:str|None=None
    event_description :str|None=None
    venue:str|None=None
    capacity:int|None=None
    event_date:date|None=None
    registration_deadline:date|None=None
    event_status:Literal['draft','published','cancelled','completed']|None=None



@create.post("/events")
def create_events(event:CreateEvent,user_id:int=Depends(give_access)):
    con=get_connection()
    cur=con.cursor(dictionary=True)

    try:
        cur.execute("select role from users where user_id=%s",(user_id,))
        row=cur.fetchone()

        if not event.registration_deadline<=event.event_date:
            raise HTTPException(
                status_code=400,
                detail="Registration deadline should be less than or equal to the event date"
        )
           
        
        if not event.capacity>=0:
            raise HTTPException(
                status_code=400,
                detail="Capacity should be greater than or equal to zero"
        )
          
        

        if row and  row["role"]=="organizer":
            cur.execute('''insert into
            events (event_name,event_description,venue,capacity,event_date,registration_deadline,event_status,organizer_id )
            values(%s,%s,%s,%s,%s,%s,%s,%s)''',
            (event.event_name,event.event_description,event.venue,event.capacity,event.event_date,event.registration_deadline,event.event_status,user_id
             ))
            con.commit()
            return {
                "message": "Created successfully"
                }
        else:
            raise HTTPException(status_code=403,detail="Only organizers can post events ")
    finally:
        cur.close()
        con.close()
#  can read the info of events 

@create.get("/events")
def show_events(page:int=1,limit:int=10):
    con=get_connection()
    cur=con.cursor(dictionary=True)
    offset = (page - 1) * limit
    try:
        cur.execute("select * from events order by event_id limit %s offset %s ",(limit,offset))
        return cur.fetchall()
        
    finally:
        cur.close()
        con.close()
   

@create.patch("/events/{event_id}")
def update_events(event_id:int,events:UpdateEvent,user_id:int=Depends(give_access)):

    update=events.model_dump(exclude_unset=True)
    if not update:
        raise HTTPException(
             status_code=400,
             detail="No fields provided for update"
        )
    con=get_connection()
    cur=con.cursor(dictionary=True)

    

    update_key=[]
    update_value=[]

    for key,values in update.items():
        update_key.append(f"{key}=%s")
        update_value.append(values)
    update_value.append(event_id)
    update_value=tuple(update_value)
     
    command=f""" update events set {", ".join(update_key)} where  event_id=%s"""

    cur.execute("select * from registrations where event_id=%s",(event_id,))
    registration=cur.fetchone()
    if registration:
        if "event_status" not in update and len(update_key)!=1:
            raise HTTPException(status_code=400,detail="Can only update the event status on a registered event")
        
    
    cur.execute("select * from events where event_id=%s",(event_id,))
    event_table=cur.fetchone()

    if not event_table:
            raise HTTPException(status_code=404, detail="Event not found")

    if "capacity" in update:
       if not update["capacity"]>=0:
            raise HTTPException(
                status_code=400,
                detail="Capacity should be greater than or equal to zero"
        )
       
    if "registration_deadline" in update :
        if "event_date" in update:
            if not update["registration_deadline"]<=update["event_date"]:
                raise HTTPException(
                    status_code=400,
                    detail="Registration deadline should be less than or equal to the event date"
                    )
        else:
            if not update["registration_deadline"]<=event_table["event_date"]:
                raise HTTPException(
                    status_code=400,
                    detail="Registration deadline should be less than or equal to the event date"
                    )
            
    elif "event_date" in update:
        if  update["event_date"]<event_table["registration_deadline"]:
            raise HTTPException(
                    status_code=400,
                    detail="Registration deadline should be less than or equal to the event date"
                    )
        
    


            

    try:
        cur.execute("select role from users where user_id=%s",(user_id,))
        row=cur.fetchone()
       

        
        
        if row and  row["role"]=="organizer" and event_table["organizer_id"]==user_id :
            cur.execute(command,update_value)
            

        else:
            raise HTTPException(status_code=403,detail="Forbidden")
        con.commit()
        return {"msg":"Updated successfully"}

    except:
        con.rollback()
        raise
        
    finally:
        cur.close()
        con.close()


# need to add delete event option 

@create.delete("/events/{event_id}")

def delete_events(event_id:int,user_id:int=Depends(give_access)):
    con=get_connection()
    cur=con.cursor(dictionary=True)
    cur.execute("select * from registrations where event_id=%s",(event_id,))
    registration=cur.fetchone()
    if registration:
        raise HTTPException(status_code=400,detail="The event has alredy Registered ")

    try:
        cur.execute("select role from users where user_id=%s",(user_id,))
        row=cur.fetchone()
        cur.execute("select organizer_id from events where event_id=%s",(event_id,))
        organizer_id=cur.fetchone()
        if not organizer_id:
            raise HTTPException(status_code=404, detail="Event not found")

        if (row["role"]=="organizer"and organizer_id["organizer_id"]==user_id) or row["role"]=="admin" :
            cur.execute("delete from events where event_id=%s",(event_id,))

        else:
            raise HTTPException( status_code=403,detail="Forbidden")
        
        con.commit()
        return {"msg":"Delted successfully"}

    finally:
        cur.close()
        con.close()