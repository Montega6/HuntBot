import os
import re
import requests
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Słowa kluczowe odrzucające akcesoria i części
EXCLUDED_KEYWORDS = [
    "etui", "case", "kabura", "szkło", "folia", "kabel", "ładowarka", 
    "pudełko", "kartonik", "uszkodzony", "na części", "icloud", "zamienię", "wymienię", "blot"
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
    # Pobieranie publicznych danych / wyszukiwanie z OLX dla konkretnego modelu
    prices = []
    try:
        url = f"https://www.olxis.pl/api/v1/offers/?query={model_name.replace(' ', '%20')}&category_id=90" # Przykładowy endpoint / zapytanie
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # POBIERANIE Z OLX (Używamy oficjalnego lub publicznego zapytania wyszukiwania)
        search_url = f"https://www.olx.pl/elektronika/telefony-komorkowe/q-{model_name.lower().replace(' ', '-')}/"
        
        # Dla celów demonstracyjnych bota w GitHub Actions (który może napotkać blokady anty-botowe OLX):
        # Pobieramy ogłoszenia przez publiczne API wyszukiwania lub parsowanie
        response = requests.get(f"https://www.olx.pl/api/v1/offers?query={model_name}&limit=50", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        
        if response.status_code == 200:
            data = response.json().get("data", [])
            for item in data:
                title = item.get("title", "")
                params = item.get("params", [])
                
                # Sprawdzenie ceny
                price_val = 0
                for p in params:
                    if p.get("key") == "price":
                        price_val = float(p.get("value", {}).get("integerValue", 0))
                
                if price_val > 300 and is_valid_phone(title): # Odrzucamy podejrzanie tanie (części/akcesoria)
                    prices.append(price_val)
    except Exception as e:
        print(f"Błąd pobierania dla {model_name}: {e}")
        
    return prices

def update_market_averages():
    print("Rozpoczynam pobieranie i przeliczanie cen z OLX...")

    for model in IPHONE_MODELS:
        print(f"Analizuję model: {model}")
        prices = fetch_olx_offers_for_model(model)
        
        if prices:
            avg_price = int(sum(prices) / len(prices))
            offers_count = len(prices)
        else:
            avg_price = 0
            offers_count = 0
            
        try:
            supabase.table("market_averages").upsert({
                "model": model,
                "avg_price": avg_price,
                "offers_count": offers_count
            }, on_conflict=["model"]).execute()
            print(f"-> Zapisano {model}: średnia {avg_price} zł ({offers_count} ofert)")
        except Exception as e:
            print(f"Błąd zapisu w bazie dla {model}: {e}")

if __name__ == "__main__":
    update_market_averages()
