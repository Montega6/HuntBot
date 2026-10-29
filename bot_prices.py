import os
import requests
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Słowa kluczowe odrzucające akcesoria i śmieci
EXCLUDED_KEYWORDS = [
    "etui", "case", "kabura", "szkło", "folia", "kabel", "ładowarka", 
    "pudełko", "kartonik", "uszkodzony", "na części", "icloud", "zamienię", "wymienię"
]

# Obsługiwane modele (od 12 wzwyż, w tym iPhone 17)
IPHONE_MODELS = [
    "iPhone 12", "iPhone 12 mini", "iPhone 12 Pro", "iPhone 12 Pro Max",
    "iPhone 13", "iPhone 13 mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max",
    "iPhone 17", "iPhone 17 Air", "iPhone 17 Pro", "iPhone 17 Pro Max"
]

def update_market_averages():
    print("Rozpoczynam codzienne przeliczanie średnich cen rynkowych...")

    for model in IPHONE_MODELS:
        print(f"Analizuję: {model}")
        
        # Tutaj docelowo znajdzie się logika pobierania ofert z OLX dla danego modelu,
        # odrzucania ofert zawierających słowa z EXCLUDED_KEYWORDS i liczenia średniej.
        # Na razie bot zapisuje strukturę, którą potem rozbudujemy o właściwy scraper:
        avg_price = 0  
        offers_count = 0 
        
        try:
            supabase.table("market_averages").upsert({
                "model": model,
                "avg_price": avg_price,
                "offers_count": offers_count
            }, on_conflict=["model"]).execute()
            print(f"Zaktualizowano wpis dla: {model}")
        except Exception as e:
            print(f"Błąd zapisu dla {model}: {e}")

if __name__ == "__main__":
    update_market_averages()
