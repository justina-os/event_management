#
# #cannot read the the login db 


from fastapi import APIRouter,Depends,HTTPException
from routes.loginPage import give_access
from db import get_connection
from pydantic import BaseModel
from datetime import date
from typing import Literal

attende=APIRouter()

#registering for the events ---checked 

@attende.post("/events/{event_id}/register")
def  register_for_event(event_id:int, user_id:int=Depends(give_access)):
    con=get_connection()
    cur=con.cursor(dictionary=True)

    #need to check the capacity of the event -- checked
    # need to check the deadline  --- checked 

    cur.execute(
    "SELECT * FROM registrations WHERE user_id=%s AND event_id=%s",
    (user_id, event_id)
    )

    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Already registered")
    
    cur.execute("select capacity , registration_deadline,event_status  from events where event_id=%s",(event_id,))
    details=cur.fetchone()
    

    try:
        if not details:
            raise HTTPException(status_code=404, detail="Event not found")
        
        capacity=details["capacity"]

        if  details["event_status"]!= "published":
            
            raise HTTPException(status_code=403, detail="Event not published yet")
        

        
        if capacity <= 0:
            raise HTTPException(
            status_code=400,
            detail="Event is full"
                )

        if details["registration_deadline"] < date.today():
            raise HTTPException(
            status_code=400,
            detail="Registration deadline has passed"
        )


        cur.execute(
        "INSERT INTO registrations (user_id, event_id) VALUES (%s, %s)",
        (user_id, event_id)
        )

        cur.execute(
        "UPDATE events SET capacity=%s WHERE event_id=%s",
        (capacity - 1, event_id)
        )

        con.commit()

        return {
            "message": "Successfully registered",
            "event_id": event_id
            }
        
    except:
        con.rollback()
        raise
    finally:
        cur.close()
        con.close()
                

@attende.delete("/events/{event_id}/register")
def cancel_registration(event_id:int,user_id:int=Depends(give_access)):
    con=get_connection()
    cur=con.cursor(dictionary=True)


    cur.execute(
    "SELECT * FROM registrations WHERE user_id=%s AND event_id=%s",
    (user_id, event_id)
    )

    if not cur.fetchone():
        raise HTTPException(status_code=404, detail=" not registered")
    
    cur.execute("select capacity from events where event_id=%s",(event_id,))
    capacity=cur.fetchone()

    if not capacity:
        raise HTTPException(status_code=404,detail="Event doesn't exist")

    try:
        cur.execute("delete from registrations where  event_id=%s and user_id=%s",(event_id,user_id))
        cur.execute("UPDATE events SET capacity=%s WHERE event_id=%s ",(capacity["capacity"]+1,event_id))
        con.commit()
        return{
            "message":"Registration cancelled successfully"
        }
    

    except:
        con.rollback()
        raise


    finally:
        cur.close()
        con.close()



    