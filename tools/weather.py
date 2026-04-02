import httpx

# Координаты городов (можно расширять)
CITIES = {
    "прокопьевск": (53.8872, 86.7449),
    "москва": (55.7558, 37.6173),
    "новосибирск": (54.9885, 82.9207),
    "кемерово": (55.3908, 86.0478),
    "санкт-петербург": (59.9311, 30.3609),
}

WMO_CODES = {
    0: "ясно",
    1: "преимущественно ясно",
    2: "переменная облачность",
    3: "пасмурно",
    45: "туман",
    48: "изморозь",
    51: "лёгкая морось",
    53: "морось",
    55: "сильная морось",
    61: "лёгкий дождь",
    63: "дождь",
    65: "сильный дождь",
    71: "лёгкий снег",
    73: "снег",
    75: "сильный снег",
    80: "ливень",
    81: "сильный ливень",
    95: "гроза",
    99: "гроза с градом",
}


async def get_weather(city: str) -> str:
    city_lower = city.strip().lower()

    if city_lower in CITIES:
        lat, lon = CITIES[city_lower]
    else:
        return (
            f"⚠️ Город '{city}' не найден в базе.\n"
            f"Доступные города: {', '.join(CITIES.keys())}"
        )

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,apparent_temperature,weathercode,"
        "windspeed_10m,relativehumidity_2m,precipitation"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=Asia%2FKrasnoyarsk"
        "&forecast_days=3"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
        data = resp.json()
    except Exception as e:
        return f"⚠️ Не удалось получить погоду: {e!r}"

    cur = data.get("current", {})
    daily = data.get("daily", {})

    temp = cur.get("temperature_2m", "?")
    feels = cur.get("apparent_temperature", "?")
    wind = cur.get("windspeed_10m", "?")
    humidity = cur.get("relativehumidity_2m", "?")
    precip = cur.get("precipitation", "?")
    code = cur.get("weathercode", 0)
    condition = WMO_CODES.get(code, "неизвестно")

    # Прогноз на 3 дня
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precip_sums = daily.get("precipitation_sum", [])

    forecast_lines = []
    for i in range(min(3, len(dates))):
        forecast_lines.append(
            f"  {dates[i]}: от {min_temps[i]}°C до {max_temps[i]}°C, "
            f"осадки {precip_sums[i]} мм"
        )
    forecast_str = "\n".join(forecast_lines)

    return (
        f"🌤️ Погода в {city.capitalize()} сейчас:\n"
        f"  🌡️ Температура: {temp}°C (ощущается как {feels}°C)\n"
        f"  ☁️ Условия: {condition}\n"
        f"  💨 Ветер: {wind} км/ч\n"
        f"  💧 Влажность: {humidity}%\n"
        f"  🌧️ Осадки сейчас: {precip} мм\n\n"
        f"📅 Прогноз на 3 дня:\n{forecast_str}"
    )
