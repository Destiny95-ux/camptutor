from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get("/search")
async def search(q: str):
    try:
        url = "https://api.duckduckgo.com/"
        response = requests.get(url, params={
            "q": q,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }, headers={"User-Agent": "Mozilla/5.0"})
        
        data = response.json()
        results = []

        # main results
        for r in data.get("RelatedTopics", [])[:10]:
            if "Text" in r and "FirstURL" in r:
                results.append({
                    "title": r["Text"].split(" - ")[0],
                    "snippet": r["Text"],
                    "url": r["FirstURL"],
                    "display_url": r["FirstURL"]
                })

        return {"results": results}
    except Exception as e:
        return {"error": str(e)}
