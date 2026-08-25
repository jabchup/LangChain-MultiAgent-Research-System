from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily = TavilySearchResults(max_results = 5)

@tool
def web_search(query: str) -> str:
    """
    Search the web for information related to the query.
    """

    results = tavily.invoke({"query": query})
    print(results)

    out = []

    for r in results:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability
    """

    headers = {
        "User-Agent":(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:

        # ================================
        # FETCH PAGE
        # ================================

        response = requests.get(
            url,
            headers = headers,
            timeout = 15
        )

        response.raise_for_status()

        html = response.text

        # ================================
        # STRATEGY 01 IS trafilatura (BEST FOR article/blogs)
        # ================================

        extracted = trafilatura.extract(
            html,
            include_comments = False,
            include_tables = False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted)
            return cleaned[:5000]

        # ================================
        # STRATEGY 02 IS readability
        # ================================

        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip = True)
        return text[:5000]

        # ================================
        # STRATEGY 03 IS fallback full page extraction
        # ================================

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup([
            "script",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip = True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]

        return "Could naught extract meaningful content from page."

    except requests.exceptions.Timeout:
        return "Requests timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return("HTTP error occurred: {str(e)}")

    except Exception as e:
        return f"Could naught scrape URL: {str(e)}"
