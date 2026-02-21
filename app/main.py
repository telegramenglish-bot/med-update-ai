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
import stripe
from fastapi import Request

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

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


@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return {"error": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")

        db = SessionLocal()
        user = db.query(User).filter(User.email == customer_email).first()

        if user:
            user.subscription_plan = "pro"
            db.commit()

        db.close()

    return {"status": "success"}
