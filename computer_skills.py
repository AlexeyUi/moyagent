import os
import base64
import time
import subprocess
from io import BytesIO

def _ensure_display():
    os.environ.setdefault("DISPLAY", ":99")

def take_screenshot() -> str:
    _ensure_display()
    from Xlib import display as xdisplay, X
    from PIL import Image
    d = xdisplay.Display(os.environ.get("DISPLAY", ":99"))
    root = d.screen().root
    geom = root.get_geometry()
    raw = root.get_image(0, 0, geom.width, geom.height, X.ZPixmap, 0xFFFFFFFF)
    img = Image.frombytes("RGB", (geom.width, geom.height), raw.data, "raw", "BGRX")
    buf = BytesIO()
    img.save(buf, format="PNG")
    d.close()
    return base64.b64encode(buf.getvalue()).decode()

def _pg():
    _ensure_display()
    import pyautogui
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = False
    return pyautogui

def click(x: int, y: int, button: str = "left"):
    _pg().click(x, y, button=button)
    return f"Клик {button} по ({x}, {y})"

def double_click(x: int, y: int):
    _pg().doubleClick(x, y)
    return f"Двойной клик по ({x}, {y})"

def move_mouse(x: int, y: int):
    _pg().moveTo(x, y)
    return f"Мышь в ({x}, {y})"

def type_text(text: str):
    _pg().typewrite(text, interval=0.05)
    return f"Введён текст: {text}"

def press_key(key: str):
    pg = _pg()
    pg.hotkey(*key.split("+")) if "+" in key else pg.press(key)
    return f"Нажата клавиша: {key}"

def scroll(x: int, y: int, direction: str = "down", amount: int = 3):
    clicks = -amount if direction == "down" else amount
    _pg().scroll(clicks, x=x, y=y)
    return f"Прокрутка {direction} на {amount} в ({x}, {y})"

def open_url_in_browser(url: str):
    _ensure_display()
    env = {**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":99")}
    subprocess.Popen(['/usr/bin/chromium-browser', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-software-rasterizer', url], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"Открыт URL: {url} (браузер загружается, подождите 10 сек перед скриншотом)"

def get_screen_size() -> dict:
    _ensure_display()
    pg = _pg()
    s = pg.size()
    return {"width": s.width, "height": s.height}
