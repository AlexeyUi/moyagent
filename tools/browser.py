import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "output" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


async def browse_url(url: str, max_chars: int = 3000) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            text = await page.inner_text("body")
            await browser.close()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        result = "\n".join(lines)
        if len(result) > max_chars:
            result = result[:max_chars] + "\n\n[... текст обрезан]"
        return result
    except Exception as e:
        return "Ошибка при открытии страницы: " + str(e)


async def screenshot_url(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    filename = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50] + ".png"
    path = SCREENSHOTS_DIR / filename
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            await page.screenshot(path=str(path), full_page=False)
            await browser.close()
        return "Скриншот сохранён: output/screenshots/" + filename
    except Exception as e:
        return "Ошибка скриншота: " + str(e)


async def google_search(query: str, max_results: int = 5) -> str:
    import httpx
    from html.parser import HTMLParser

    class DDGParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.results = []
            self.in_title = False

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            if tag == "a" and "result__a" in attrs_dict.get("class", ""):
                self.in_title = True

        def handle_endtag(self, tag):
            if tag == "a" and self.in_title:
                self.in_title = False

        def handle_data(self, data):
            if self.in_title and data.strip():
                self.results.append(data.strip())

    url = "https://html.duckduckgo.com/html/?q=" + query.replace(" ", "+")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            resp = await client.post(url, data={"q": query})
        parser = DDGParser()
        parser.feed(resp.text)
        items = parser.results[:max_results]
        if not items:
            return "Результатов не найдено по запросу: " + query
        return "Результаты поиска '" + query + "':\n\n" + "\n".join(str(i+1) + ". " + t for i, t in enumerate(items))
    except Exception as e:
        return "Ошибка поиска: " + str(e)
