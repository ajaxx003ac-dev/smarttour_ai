import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from .db import Base, engine, get_db
from .models import User, Attraction, Business, Trip, Booking, Event
from .schemas import PlannerRequest, EventRequest, ChatRequest, LoginRequest, RegisterRequest
from .security import hash_password, verify_password, create_token
from .ai import build_itinerary, chat_answer
from .ai_llm import llm_enabled


Base.metadata.create_all(bind=engine)
app=FastAPI(title="SMARTTOUR AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"ok","service":"SMARTTOUR AI"}

@app.post("/api/auth/register")
def register(req:RegisterRequest,db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=req.email).first(): raise HTTPException(409,"Email already registered")
    if req.role not in ("tourist","business","admin"): raise HTTPException(400,"Invalid role")
    u=User(name=req.name,email=req.email,password_hash=hash_password(req.password),role=req.role); db.add(u); db.commit(); db.refresh(u)
    return {"token":create_token(u.id,u.role),"user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role}}

@app.post("/api/auth/login")
def login(req:LoginRequest,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(email=req.email).first()
    if not u or not verify_password(req.password,u.password_hash): raise HTTPException(401,"Invalid credentials")
    return {"token":create_token(u.id,u.role),"user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role}}


@app.get("/api/ai/status")
def ai_status():
    return {"enabled": llm_enabled(), "provider": "OpenAI Responses API" if llm_enabled() else "deterministic fallback", "model": __import__("os").getenv("LLM_MODEL", "gpt-5.6-luna")}

@app.get("/api/attractions")
def attractions(destination:str="",db:Session=Depends(get_db)):
    q=db.query(Attraction)
    if destination: q=q.filter(Attraction.destination.ilike(f"%{destination}%"))
    return [{"id":a.id,"name":a.name,"destination":a.destination,"category":a.category,"description":a.description,"lat":a.lat,"lon":a.lon,"crowd_pct":a.crowd_pct,"predicted_crowd_pct":a.predicted_crowd_pct,"capacity":a.capacity,"popularity":a.popularity,"best_time":a.best_time,"avg_cost":a.avg_cost,"safety_score":a.safety_score,"sustainability_score":a.sustainability_score} for a in q.all()]

@app.get("/api/businesses")
def businesses(destination:str="",category:str="",db:Session=Depends(get_db)):
    q=db.query(Business)
    if destination:q=q.filter(Business.destination.ilike(f"%{destination}%"))
    if category:q=q.filter(Business.category.ilike(f"%{category}%"))
    return [{"id":b.id,"name":b.name,"category":b.category,"destination":b.destination,"location":b.location,"price":b.price,"rating":b.rating,"availability":b.availability,"description":b.description,"lat":b.lat,"lon":b.lon,"bookings":b.bookings} for b in q.all()]

@app.post("/api/planner")
def planner(req:PlannerRequest,db:Session=Depends(get_db)):
    plan=build_itinerary(db,req)
    if not plan: raise HTTPException(404,"No demo attractions found for this destination")
    t=Trip(destination=req.destination,days=req.days,travelers=req.travelers,budget=req.budget,interests=req.interests,pace=req.pace,food_preferences=req.food_preferences,transport=req.transport,accessibility=req.accessibility,itinerary_json=json.dumps(plan),sustainability_score=plan["sustainability_score"])
    db.add(t); db.commit(); db.refresh(t)
    plan["trip_id"]=t.id
    return plan

@app.post("/api/trips/{trip_id}/simulate-event")
def simulate_event(trip_id:int,req:EventRequest,db:Session=Depends(get_db)):
    trip=db.get(Trip,trip_id)
    if not trip: raise HTTPException(404,"Trip not found")
    target=None
    if req.attraction_name: target=db.query(Attraction).filter(Attraction.name.ilike(f"%{req.attraction_name}%"),Attraction.destination.ilike(f"%{trip.destination}%")).first()
    if not target:
        plan=json.loads(trip.itinerary_json or '{}'); names=[i['title'] for d in plan.get('days',[]) for i in d.get('items',[])]
        if names: target=db.query(Attraction).filter(Attraction.name==names[0]).first()
    if target:
        if req.event_type in ("crowd","heavy_crowd"): target.crowd_pct=92; target.predicted_crowd_pct=95
        elif req.event_type=="rain": target.crowd_pct=15
        db.add(Event(destination=trip.destination,attraction_id=target.id,event_type=req.event_type,severity=req.severity,message=f"{req.event_type.replace('_',' ').title()} detected at {target.name}"))
    db.commit()
    req2=PlannerRequest(destination=trip.destination,days=trip.days,travelers=trip.travelers,budget=trip.budget,interests=trip.interests,pace=trip.pace,food_preferences=trip.food_preferences,transport=trip.transport,accessibility=trip.accessibility)
    optimized=build_itinerary(db,req2,avoid_crowd=True)
    optimized["trip_id"]=trip.id; optimized["event"]={"type":req.event_type,"severity":req.severity,"message":f"Your itinerary has been optimized because {target.name if target else 'conditions'} changed.","original_mode":"original","new_mode":"optimized"}
    trip.itinerary_json=json.dumps(optimized); trip.sustainability_score=optimized["sustainability_score"]; db.commit()
    return optimized

@app.post("/api/assistant")
def assistant(req:ChatRequest,db:Session=Depends(get_db)): return {"answer":chat_answer(db,req.message,req.destination),"source":"OpenAI Responses API + grounded SmartTour tourism data" if llm_enabled() else "SmartTour tourism data + deterministic fallback"}

@app.post("/api/bookings")
def booking(business_id:int,tourist_name:str,amount:float,trip_id:int|None=None,db:Session=Depends(get_db)):
    b=db.get(Business,business_id)
    if not b or not b.availability: raise HTTPException(400,"Business unavailable")
    b.bookings += 1; item=Booking(business_id=business_id,tourist_name=tourist_name,amount=amount,trip_id=trip_id); db.add(item); db.commit(); db.refresh(item)
    return {"booking_id":item.id,"status":item.status,"business":b.name,"amount":amount}

@app.get("/api/admin/overview")
def admin_overview(db:Session=Depends(get_db)):
    ats=db.query(Attraction).all(); bs=db.query(Business).all(); bookings=db.query(Booking).count()
    return {"tourists":db.query(User).filter_by(role="tourist").count()+1240,"businesses":len(bs),"bookings":bookings+428,"revenue":sum(b.amount for b in db.query(Booking).all())+842500,"attractions":len(ats),"avg_crowd":round(sum(a.crowd_pct for a in ats)/max(1,len(ats))),"occupancy":74,"sustainability":84,"crowd_data":[{"name":a.name,"crowd":a.crowd_pct,"lat":a.lat,"lon":a.lon} for a in ats],"destinations":[{"name":d,"tourists":v} for d,v in [("Jaipur",34),("Agra",27),("Goa",21),("Kerala",13),("Chennai",5)]]}

@app.get("/api/business/dashboard")
def business_dashboard(db:Session=Depends(get_db)):
    bs=db.query(Business).all(); total=sum(b.bookings for b in bs)
    return {"bookings":total+186,"occupancy":78,"demand":86,"revenue":sum(b.price*b.bookings for b in bs)+318000,"preferences":{"family":38,"food":27,"heritage":22,"adventure":13},"recommendation":"Expected tourist demand is high this weekend. Consider creating a family heritage package with a local food experience."}

@app.get("/api/safety")
def safety(destination:str="Jaipur",db:Session=Depends(get_db)):
    return {"destination":destination,"safety_score":92,"emergency":[{"label":"Police","number":"112"},{"label":"Ambulance","number":"108"},{"label":"Tourist Helpline","number":"1363"}],"nearby":[{"name":"Government Hospital","distance":"2.1 km"},{"name":"City Police Station","distance":"1.4 km"}],"message":"Demo safety layer. Real emergency routing/location sharing can be connected later."}

@app.on_event("startup")
def startup():
    from .seed import seed
    seed()
