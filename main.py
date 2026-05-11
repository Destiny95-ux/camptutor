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
        url = "https://duckduckgo.com/html/"
        response = requests.get(
            url,
            params={"q": q},
            headers={"User-Agent": "Mozilla/5.0"}
        )
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.select(".result")[:10]:  # increase limit here
            title = result.select_one(".result__title")
            snippet = result.select_one(".result__snippet")
            link = result.select_one(".result__url")
            anchor = result.select_one(".result__title a")

            # get the real href from the anchor tag
            href = anchor["href"] if anchor and anchor.get("href") else None

            # duckduckgo wraps links, extract the actual URL
            if href and href.startswith("//duckduckgo.com/l/"):
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(href)
                actual_url = parse_qs(parsed.query).get("uddg", [href])[0]
            else:
                actual_url = href

            results.append({
                "title": title.get_text(strip=True) if title else "No title",
                "snippet": snippet.get_text(strip=True) if snippet else "No snippet",
                "url": actual_url,
                "display_url": link.get_text(strip=True) if link else actual_url,
            })
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}
