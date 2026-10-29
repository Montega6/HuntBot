import os
import requests
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Słowa kluczowe odrzucające akcesoria, uszkodzone sztuki i śmieci
EXCLUDED_KEYWORDS = [
    "etui", "case", "kabura", "szkło", "folia", "kabel", "ładowarka", 
    "pudełko", "kartonik", "uszkodzony", "na części", "icloud", "zamienię", "wymienię", "blot", "mały ekran"
]

IPHONE_MODELS = [
    "iPhone 12", "iPhone 12 mini", "iPhone 12 Pro", "iPhone 12 Pro Max",
    "iPhone 13", "iPhone 13 mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max",
    "iPhone 17", "iPhone 17 Air", "iPhone 17 Pro", "iPhone 17 Pro Max"
]

def is_valid_phone(title):
    title_lower = title.lower()
    for word in EXCLUDED_KEYWORDS:
        if word in title_lower:
            return False
    return True

def fetch_allegro_offers_for_model(model_name):
    prices = []
    try:
        # Publiczne zapytanie do wyszukiwarki ofert Allegro
        url = f"https://allegro.pl/listing?string={model_name.replace(' ', '%20')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "pl-PL,pl;q=0.9"
        }
        
        # Pobieramy stronę wyników wyszukiwania Allegro i parsujemy ceny przez publiczne zapytanie lub API
        # Możemy też skorzystać z publicznego endpointu sugerującego oferty lub API Allegro REST
        api_url = f"https://allegro.pl/api/listing?string={model_name.replace(' ', '%20')}&limit=50"
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Przeszukujemy strukturę JSON z wynikami Allegro
            items = data.get("items", {}).get("regular", [])
            for item in items:
                title = item.get("title", "")
                price_data = item.get("sellingMode", {}).get("price", {})
                price_val = float(price_data.get("amount", 0))
                
                # Walidacja ceny (np. powyżej 500 zł, żeby odrzucić etui) oraz filtrowanie słów
                if price_val > 500 and is_valid_phone(title):
                    prices.append(price_val)
        else:
            print(f"Ostrzeżenie: Allegro zwróciło status {response.status_code} dla {model_name}")
            
    except Exception as e:
        print(f"Błąd pobierania z Allegro dla {model_name}: {e}")
        
    return prices

def update_market_averages():
    print("Rozpoczynam pobieranie i przeliczanie cen z Allegro...")

    for model in IPHONE_MODELS:
        print(f"Analizuję model: {model}")
        prices = fetch_allegro_offers_for_model(model)
        
        if prices and len(prices) > 0:
            avg_price = int(sum(prices) / len(prices))
            offers_count = len(prices)
            print(f"-> Znaleziono {offers_count} ofert, średnia: {avg_price} zł")
        else:
            avg_price = 0
            offers_count = 0
            print(f"-> Brak danych dla {model}")
            
        try:
            supabase.table("market_averages").upsert({
                "model": model,
                "avg_price": avg_price,
                "offers_count": offers_count
            }, on_conflict=["model"]).execute()
            print(f"Zaktualizowano bazę dla: {model}")
        except Exception as e:
            print(f"Błąd zapisu w bazie dla {model}: {e}")

if __name__ == "__main__":
    update_market_averages()
