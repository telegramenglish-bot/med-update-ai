from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .database import engine
from .models import Base, Article
from .scheduler import start_scheduler
from sqlalchemy.orm import Session
from .database import SessionLocal

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
