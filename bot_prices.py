import os
import re
import requests
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

EXCLUDED_KEYWORDS = [
    "etui", "case", "kabura", "szkło", "folia", "kabel", "ładowarka", 
    "pudełko", "kartonik", "uszkodzony", "na części", "icloud", "zamienię", "wymienię"
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

def fetch_olx_offers_for_model(model_name):
    prices = []
    try:
        # Używamy nagłówków imitujących prawdziwą przeglądarkę, aby ominąć podstawowe filtry
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.olx.pl/"
        }
        
        # Pobieramy zapytanie z mobilnego/publicznego API wyszukiwania OLX
        search_query = model_name.replace(" ", "%20")
        url = f"https://www.olx.pl/api/v1/offers?query={search_query}&limit=50&category_id=90"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get("data", [])
            for item in data:
                title = item.get("title", "")
                params = item.get("params", [])
                
                price_val = 0
                for p in params:
                    if p.get("key") == "price":
                        val_dict = p.get("value", {})
                        if isinstance(val_dict, dict):
                            price_val = float(val_dict.get("integerValue", 0))
                        elif isinstance(val_dict, (int, float)):
                            price_val = float(val_dict)
                
                # Walidacja ceny (np. powyżej 400 zł, żeby odrzucić oczywiste śmieci) oraz filtr słów kluczowych
                if price_val > 400 and is_valid_phone(title):
                    prices.append(price_val)
        else:
            print(f"Ostrzeżenie: OLX zwrócił kod statusu {response.status_code} dla {model_name}")
            
    except Exception as e:
        print(f"Błąd pobierania dla {model_name}: {e}")
        
    return prices

def update_market_averages():
    print("Rozpoczynam pobieranie i przeliczanie cen z OLX...")

    for model in IPHONE_MODELS:
        print(f"Analizuję model: {model}")
        prices = fetch_olx_offers_for_model(model)
        
        if prices and len(prices) > 0:
            avg_price = int(sum(prices) / len(prices))
            offers_count = len(prices)
            print(f"-> Znaleziono {offers_count} ofert, średnia: {avg_price} zł")
        else:
            # Jeśli GitHub Actions chwilowo nie może sparsować OLX, ustawiamy bezpieczne dane zapasowe,
            # żeby tabela na stronie nie świeciła pustkami
            avg_price = 0
            offers_count = 0
            print(f"-> Brak danych z API dla {model}")
            
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
