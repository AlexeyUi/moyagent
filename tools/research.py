import httpx
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.urls = []
        self.in_title = False
        self.current_url = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "a" and "result__a" in attrs_dict.get("class", ""):
            self.in_title = True
            self.current_url = attrs_dict.get("href", "")

    def handle_endtag(self, tag):
        if tag == "a" and self.in_title:
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and data.strip():
            self.results.append(data.strip())
            self.urls.append(self.current_url)


async def search_and_summarize(query: str, llm_func) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    search_url = "https://html.duckduckgo.com/html/?q=" + query.replace(" ", "+")

    try:
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            resp = await client.post(search_url, data={"q": query})
    except Exception as e:
        return "Ошибка поиска: " + str(e)

    parser = DDGParser()
    parser.feed(resp.text)
    titles = parser.results[:5]

    if not titles:
        return "Ничего не найдено по запросу: " + query

    titles_text = "\n".join(str(i+1) + ". " + t for i, t in enumerate(titles))

    prompt = [
        {
            "role": "system",
            "content": (
                "Ты — аналитический ассистент. "
                "Пользователь ищет информацию в интернете. "
                "Ниже — заголовки найденных страниц. "
                "Сделай краткую выжимку: что нашлось, какие ресурсы стоит изучить, "
                "и дай 2-3 практических совета по теме. "
                "Отвечай по-русски, кратко и по делу."
            ),
        },
        {
            "role": "user",
            "content": "Запрос: " + query + "\n\nНайдено:\n" + titles_text,
        },
    ]

    try:
        summary = llm_func(prompt)
    except Exception as e:
        summary = "Ошибка LLM: " + str(e)

    return (
        "Поиск по: " + query + "\n\n"
        "Найденные страницы:\n" + titles_text + "\n\n"
        "Выжимка:\n" + summary
    )


async def read_and_summarize(url: str, question: str, llm_func) -> str:
    import httpx
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts = []
            self.skip_tags = {"script", "style", "nav", "footer", "head"}
            self.current_skip = False
            self.skip_depth = 0

        def handle_starttag(self, tag, attrs):
            if tag in self.skip_tags:
                self.current_skip = True
                self.skip_depth += 1

        def handle_endtag(self, tag):
            if tag in self.skip_tags:
                self.skip_depth -= 1
                if self.skip_depth <= 0:
                    self.current_skip = False
                    self.skip_depth = 0

        def handle_data(self, data):
            if not self.current_skip:
                text = data.strip()
                if len(text) > 30:
                    self.text_parts.append(text)

    if not url.startswith("http"):
        url = "https://" + url

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        async with httpx.AsyncClient(timeout=15, headers=headers, follow_redirects=True) as client:
            resp = await client.get(url)
        parser = TextExtractor()
        parser.feed(resp.text)
        page_text = " ".join(parser.text_parts)
        page_text = page_text[:4000]
    except Exception as e:
        return "Ошибка при чтении страницы: " + str(e)

    if not page_text.strip():
        return "Не удалось извлечь текст со страницы: " + url

    prompt = [
        {
            "role": "system",
            "content": (
                "Ты — аналитический ассистент Danny. "
                "Пользователь открыл страницу и хочет получить выжимку. "
                "Отвечай по-русски, кратко и конкретно."
            ),
        },
        {
            "role": "user",
            "content": (
                "Страница: " + url + "\n\n"
                "Вопрос/задача: " + question + "\n\n"
                "Содержимое страницы:\n" + page_text
            ),
        },
    ]

    try:
        summary = llm_func(prompt)
        return "Страница: " + url + "\n\nВыжимка:\n" + summary
    except Exception as e:
        return "Ошибка LLM: " + str(e)
