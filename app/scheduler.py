from apscheduler.schedulers.background import BackgroundScheduler
from .pubmed import fetch_pubmed
from .ai_engine import summarize, translate
from .database import SessionLocal
from .models import Article

specialties = {
    "cardiology": "heart failure OR cardiology",
    "ai_medicine": "artificial intelligence medicine",
    "oncology": "cancer clinical trial"
}

def update_articles():
    db = SessionLocal()
    
    for specialty, query in specialties.items():
        articles = fetch_pubmed(query)
        
        for title, abstract in articles:
            summary = summarize(abstract)
            translated = translate(summary)
            
            new_article = Article(
                title=title,
                specialty=specialty,
                summary=summary,
                translated_summary=translated
            )
            
            db.add(new_article)
    
    db.commit()
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_articles, "interval", hours=24)
    scheduler.start()
