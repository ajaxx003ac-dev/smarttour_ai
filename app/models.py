from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="tourist")

class Attraction(Base):
    __tablename__ = "attractions"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    destination = Column(String(100), nullable=False)
    category = Column(String(80), nullable=False)
    description = Column(Text)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    crowd_pct = Column(Integer, default=30)
    predicted_crowd_pct = Column(Integer, default=35)
    capacity = Column(Integer, default=1000)
    popularity = Column(Integer, default=70)
    best_time = Column(String(60), default="08:00–10:00")
    open_hours = Column(String(80), default="09:00–18:00")
    avg_cost = Column(Float, default=100)
    safety_score = Column(Integer, default=90)
    sustainability_score = Column(Integer, default=80)

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    category = Column(String(60), nullable=False)
    destination = Column(String(100), nullable=False)
    location = Column(String(180))
    price = Column(Float, default=500)
    rating = Column(Float, default=4.2)
    availability = Column(Boolean, default=True)
    description = Column(Text)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    bookings = Column(Integer, default=0)

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True)
    tourist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    destination = Column(String(100), nullable=False)
    days = Column(Integer, nullable=False)
    travelers = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    interests = Column(String(255), default="history,food")
    pace = Column(String(40), default="relaxed")
    food_preferences = Column(String(120), default="local")
    transport = Column(String(60), default="public")
    accessibility = Column(String(120), default="none")
    itinerary_json = Column(Text)
    sustainability_score = Column(Integer, default=80)
    status = Column(String(40), default="active")
    created_at = Column(DateTime, server_default=func.now())

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, nullable=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    tourist_name = Column(String(120), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(30), default="confirmed")
    created_at = Column(DateTime, server_default=func.now())

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    destination = Column(String(100), nullable=False)
    attraction_id = Column(Integer, nullable=True)
    event_type = Column(String(60), nullable=False)
    severity = Column(String(30), default="medium")
    message = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
