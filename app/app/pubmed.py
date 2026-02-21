import requests
from xml.etree import ElementTree

def fetch_pubmed(query, max_results=3):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
    search_response = requests.get(search_url).json()
    
    ids = ",".join(search_response["esearchresult"]["idlist"])
    
    fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
    fetch_response = requests.get(fetch_url)
    
    root = ElementTree.fromstring(fetch_response.content)
    
    articles = []
    
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        abstract = article.findtext(".//AbstractText")
        
        if abstract:
            articles.append((title, abstract))
    
    return articles
