import json
from .db import Base, engine, SessionLocal
from .models import User, Attraction, Business, Trip, Booking
from .security import hash_password

DESTS = {
 "Jaipur": [26.9855,75.8513], "Agra":[27.1751,78.0421], "Goa":[15.2993,74.1240], "Kerala":[9.9312,76.2673], "Chennai":[13.0827,80.2707]
}
ATTRACTIONS = [
 ("Amber Fort","Jaipur","history","Hilltop fort with panoramic views",26.9855,75.8513,72,68,5000,96,"08:00–10:00",200,91,78),
 ("City Palace","Jaipur","history","Royal residence and museum",26.9258,75.8237,48,55,2500,88,"09:00–11:00",300,94,84),
 ("Jantar Mantar","Jaipur","history","UNESCO astronomical observatory",26.9247,75.8246,39,44,1200,82,"16:00–18:00",100,95,89),
 ("Hawa Mahal","Jaipur","culture","Iconic pink sandstone facade",26.9239,75.8267,61,65,2000,92,"08:00–09:30",100,93,80),
 ("Albert Hall Museum","Jaipur","culture","Decorative arts and heritage museum",26.9115,75.8197,31,38,1600,76,"15:00–17:00",200,96,90),
 ("Taj Mahal","Agra","history","World-famous marble monument",27.1751,78.0421,92,88,20000,100,"06:00–08:00",1100,96,64),
 ("Agra Fort","Agra","history","Mughal fort overlooking the Yamuna",27.1795,78.0211,35,41,9000,86,"08:00–10:00",650,94,75),
 ("Mehtab Bagh","Agra","nature","Garden with Taj Mahal views",27.1799,78.0422,22,28,2500,70,"17:00–18:30",200,92,93),
 ("Fort Kochi","Kerala","culture","Historic waterfront district",9.9667,76.2425,40,45,4000,84,"07:00–10:00",0,94,91),
 ("Mattancherry Palace","Kerala","history","Heritage palace and murals",9.9594,76.2594,28,35,1200,73,"10:00–12:00",50,96,90),
 ("Baga Beach","Goa","beach","Popular beach with water activities",15.5557,73.7517,77,73,8000,94,"16:00–18:00",0,88,72),
 ("Fontainhas","Goa","culture","Latin Quarter with heritage streets",15.4966,73.8282,33,39,2500,75,"08:00–10:00",0,95,92),
 ("Marina Beach","Chennai","beach","Long urban beachfront",13.0500,80.2824,69,71,15000,95,"06:00–08:00",0,88,70),
 ("Kapaleeshwarar Temple","Chennai","culture","Historic Dravidian temple",13.0339,80.2699,45,52,3000,88,"06:30–08:30",0,94,85),
]
BUSINESSES = [
 ("Pink City Heritage Homestay","Homestay","Jaipur","Bani Park",1800,4.7,26.919,75.793,"Family-friendly heritage stay"),
 ("Rajasthani Rasoi","Restaurant","Jaipur","MI Road",450,4.6,26.915,75.807,"Authentic thali and local desserts"),
 ("Royal Trails Jaipur","Tour guide","Jaipur","Old City",900,4.8,26.923,75.826,"Certified local heritage guide"),
 ("Amber Local Crafts","Handicraft","Jaipur","Amer",650,4.5,26.985,75.851,"Artisan-made textiles and blue pottery"),
 ("Agra Spice Kitchen","Restaurant","Agra","Taj East Gate",400,4.5,27.171,78.042,"Local Mughlai and vegetarian dishes"),
 ("Yamuna Heritage Walks","Tour guide","Agra","Agra Fort",800,4.7,27.179,78.021,"Small-group heritage walks"),
 ("Kerala Backwater Haven","Homestay","Kerala","Fort Kochi",2200,4.8,9.967,76.243,"Locally hosted cultural stay"),
 ("Coconut Leaf Experiences","Cultural experience","Kerala","Mattancherry",1200,4.9,9.959,76.259,"Cooking and craft workshop"),
 ("Goan Home Table","Restaurant","Goa","Panaji",500,4.7,15.49,73.83,"Home-style Goan cuisine"),
 ("Fontainhas Storytellers","Tour guide","Goa","Fontainhas",700,4.8,15.497,73.828,"Walking tours by local storytellers"),
 ("Marina Local Eats","Restaurant","Chennai","Triplicane",350,4.5,13.055,80.276,"South Indian breakfast and snacks"),
 ("Madras Heritage Trails","Tour guide","Chennai","Mylapore",600,4.7,13.034,80.27,"Temple and architecture walks"),
]

def seed():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    if db.query(User).count()==0:
        db.add_all([User(name="Demo Tourist",email="tourist@smarttour.ai",password_hash=hash_password("demo123"),role="tourist"), User(name="Demo Business",email="business@smarttour.ai",password_hash=hash_password("demo123"),role="business"), User(name="Demo Admin",email="admin@smarttour.ai",password_hash=hash_password("demo123"),role="admin")])
    if db.query(Attraction).count()==0:
        for r in ATTRACTIONS: db.add(Attraction(name=r[0],destination=r[1],category=r[2],description=r[3],lat=r[4],lon=r[5],crowd_pct=r[6],predicted_crowd_pct=r[7],capacity=r[8],popularity=r[9],best_time=r[10],avg_cost=r[11],safety_score=r[12],sustainability_score=r[13]))
    if db.query(Business).count()==0:
        for r in BUSINESSES: db.add(Business(name=r[0],category=r[1],destination=r[2],location=r[3],price=r[4],rating=r[5],lat=r[6],lon=r[7],description=r[8]))
    db.commit(); db.close()

if __name__ == "__main__": seed()
