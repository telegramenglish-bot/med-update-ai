from fastapi import FastAPI
import requests
from xml.etree import ElementTree
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_pubmed(query="AI in medicine", max_results=3):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
    search_response = requests.get(search_url).json()
    
    id_list = search_response["esearchresult"]["idlist"]
    ids = ",".join(id_list)
    
    fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
    fetch_response = requests.get(fetch_url)
    
    root = ElementTree.fromstring(fetch_response.content)
    
    articles = []
    
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        abstract = article.findtext(".//AbstractText")
        
        if abstract:
            articles.append({
                "title": title,
                "abstract": abstract
            })
    
    return articles


def summarize_text(text):
    prompt = f"""
    Resume el siguiente abstract médico en:
    1. 5 puntos clave
    2. Aplicación clínica
    3. Nivel de evidencia
    
    Texto:
    {text}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response["choices"][0]["message"]["content"]


@app.get("/update")
def update():
    articles = fetch_pubmed()
    results = []
    
    for article in articles:
        summary = summarize_text(article["abstract"])
        
        results.append({
            "title": article["title"],
            "summary": summary
        })
    
    return {"updates": results}


from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .models import User
from .auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    
    db_user = User(
        email=user.email,
        password=hash_password(user.password)
    )
    
    db.add(db_user)
    db.commit()
    db.close()
    
    return {"message": "User created"}

@app.post("/login")
def login(user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": db_user.email})
    db.close()
    
    return {"access_token": token}

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
