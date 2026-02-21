from fastapi import FastAPI, Request
from .payments import create_checkout_session
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .database import engine
from .models import Base, Article
from .scheduler import start_scheduler
from sqlalchemy.orm import Session
from .database import SessionLocal
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

start_scheduler()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db: Session = SessionLocal()
    articles = db.query(Article).order_by(Article.created_at.desc()).limit(20).all()
    db.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "articles": articles
    })

from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    email: str

@app.post("/create-checkout")
def create_checkout(data: CheckoutRequest):
    price_id = os.getenv("STRIPE_PRICE_ID")
    
    if not price_id:
        raise HTTPException(status_code=500, detail="Stripe price ID not configured")
    
    checkout_url = create_checkout_session(data.email, price_id)
    
    return {"checkout_url": checkout_url}
