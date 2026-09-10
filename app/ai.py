import json, re
from sqlalchemy.orm import Session
from .models import Attraction, Business
from .ai_llm import polish_itinerary, answer_with_llm

def rank_attractions(db: Session, destination: str, interests: str, budget: float, travelers: int, avoid_crowd=False):
    rows=db.query(Attraction).filter(Attraction.destination.ilike(f"%{destination}%")).all()
    interest_set={x.strip().lower() for x in interests.split(',') if x.strip()}
    scored=[]
    for a in rows:
        pref=100 if a.category.lower() in interest_set else 65
        budget_match=max(0,100-(a.avg_cost*travelers/max(budget,1))*100)
        distance=80
        crowd=max(0,100-a.crowd_pct) if avoid_crowd else max(0,100-0.5*a.crowd_pct)
        score=0.30*pref+0.15*budget_match+0.10*distance+0.15*a.safety_score+0.15*a.sustainability_score+0.15*crowd
        scored.append((score,a))
    return [a for _,a in sorted(scored,key=lambda x:x[0],reverse=True)]

def recommend_businesses(db,destination,category=None,budget=999999):
    q=db.query(Business).filter(Business.destination.ilike(f"%{destination}%"),Business.availability==True,Business.price<=budget)
    if category: q=q.filter(Business.category.ilike(f"%{category}%"))
    return sorted(q.all(),key=lambda b:(b.rating,-b.price),reverse=True)

def build_itinerary(db, req, avoid_crowd=False):
    attractions=rank_attractions(db,req.destination,req.interests,req.budget,req.travelers,avoid_crowd)[:max(req.days*2,3)]
    if not attractions: return None
    daily=[]
    per_day=max(1,min(3,len(attractions)//req.days if len(attractions)>=req.days else 1))
    for d in range(req.days):
        chunk=attractions[d*per_day:(d+1)*per_day]
        if not chunk and attractions: chunk=[attractions[-1]]
        items=[]
        for i,a in enumerate(chunk):
            meal=recommend_businesses(db,req.destination,"Restaurant",500)
            restaurant=meal[(d+i)%len(meal)] if meal else None
            items.append({"time": ["08:30","11:30","16:00"][i%3],"title":a.name,"type":"attraction","lat":a.lat,"lon":a.lon,"duration":"1.5–2.5 hrs","travel_time":"20–35 min","cost":round(a.avg_cost),"crowd":a.crowd_pct,"safety":a.safety_score,"sustainability":a.sustainability_score,"reason":f"Matches {a.category} interest; crowd is {a.crowd_pct}%.","restaurant": restaurant.name if restaurant else None})
        daily.append({"day":d+1,"title":f"Day {d+1} · {req.destination}","items":items})
    total=sum(i["cost"] for day in daily for i in day["items"])+req.travelers*300*req.days
    local_count=sum(1 for b in recommend_businesses(db,req.destination,"Restaurant",500)[:3])
    crowd_bonus=10 if avoid_crowd else 5
    sustainability=max(50,min(98,round(70 + (10 if req.transport in ['public','walking','mixed'] else 0)+crowd_bonus+min(local_count*3,9))))
    plan={"destination":req.destination,"days":daily,"estimated_total":round(total),"budget":req.budget,"sustainability_score":sustainability,"mode":"optimized" if avoid_crowd else "original","ai_note":"Grounded recommendation engine using preference, budget, distance, availability, safety, sustainability and crowd signals."}
    return polish_itinerary(plan, req)

def chat_answer(db,message,destination):
    attractions = db.query(Attraction).filter(Attraction.destination.ilike(f"%{destination}%")).all()[:20]
    businesses = db.query(Business).filter(Business.destination.ilike(f"%{destination}%")).all()[:20]
    context={"attractions":[{"name":a.name,"category":a.category,"crowd_pct":a.crowd_pct,"best_time":a.best_time,"cost":a.avg_cost,"safety":a.safety_score,"sustainability":a.sustainability_score} for a in attractions],"businesses":[{"name":b.name,"category":b.category,"price":b.price,"rating":b.rating,"availability":b.availability} for b in businesses]}
    llm_answer=answer_with_llm(message,destination,context)
    if llm_answer:
        return llm_answer
    m=message.lower()
    if "rain" in m or "rainy" in m: return "If it rains, switch outdoor attractions to museums and heritage interiors. In the current demo, Albert Hall Museum and City Palace are strong weather-resilient choices."
    if "crowd" in m or "less crowded" in m: 
        ats=rank_attractions(db,destination,"history,culture",5000,2,True)[:3]
        return "Less-crowded picks: " + ", ".join(f"{a.name} ({a.crowd_pct}%)" for a in ats) + ". I prioritize lower crowd while preserving safety and interest match."
    if "restaurant" in m:
        nums=re.findall(r"\d+",message); budget=float(nums[0]) if nums else 500
        bs=recommend_businesses(db,destination,"Restaurant",budget)[:3]
        return "Restaurants within your budget: " + ", ".join(f"{b.name} ₹{int(b.price)} (★{b.rating})" for b in bs) if bs else "I could not find a demo restaurant under that budget in this destination."
    if "airport" in m: return "For the prototype, use public transport where practical; the route recommendation weighs time, safety and sustainability. Real transit APIs can be plugged into the same service later."
    return "I can optimize your trip for crowd, rain, budget, food, accessibility or local experiences. Try: 'What can I do if it rains?' or 'Find a restaurant under ₹500'."
