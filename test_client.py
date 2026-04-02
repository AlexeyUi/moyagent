import requests

base_url = "http://localhost:8000"

# Простейший запрос к корню
r = requests.get(base_url)
print("GET /:", r.status_code, r.text[:500])

# Попробуем /docs
r2 = requests.get(base_url + "/docs")
print("GET /docs:", r2.status_code, r2.text[:500])
