import os
import sys
import time
import requests
import urllib.parse
import random
import re
import concurrent.futures
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

# Inicjalizacja kolorów
init(autoreset=True)

# Lista User-Agentów do rotacji
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
]

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = f"""{Fore.MAGENTA}
  __  __                       ____  _    _     _     _                     
 |  \/  | ___  _ __   ___ _ __/ ___|| | _(_) __| | __| |_ __ ___   __ ___  __
 | |\/| |/ _ \| '_ \ / _ \ '__\___ \| |/ / |/ _` |/ _` | '_ ` _ \ / _` \ \/ /
 | |  | | (_) | | | |  __/ |   ___) |   <| | (_| | (_| | | | | | | (_| |>  < 
 |_|  |_|\___/|_| |_|\___|_|  |____/|_|\_\_|\__,_|\__,_|_| |_| |_|\__,_/_/\_/
{Style.RESET_ALL}
    {Fore.CYAN}[+] Wersja: v2.1 PROXY & BYPASS EDITION
    [+] Credits: @monerthetimeprojector 
    [+] Ulepszone: Bypass Cookies, Agresywny Regex, Proxy Checker
    {Style.RESET_ALL}"""
    print(banner)

# ================= PROXY SYSTEM =================

def get_free_proxies():
    print(f"\n{Fore.YELLOW}[*] Pobieranie darmowych proxy...{Style.RESET_ALL}")
    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        response = requests.get(url, timeout=10)
        proxies = response.text.strip().split("\r\n")
        proxies = [p for p in proxies if p]
        print(f"{Fore.GREEN}[+] Pobrano {len(proxies)} proxy do sprawdzenia.{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}[!] Błąd pobierania proxy: {e}{Style.RESET_ALL}")
        return []

def check_proxy(proxy):
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    try:
        requests.get("https://www.google.com", proxies=proxies, timeout=5)
        return proxy
    except:
        return None

def check_and_filter_proxies(proxies, limit=15):
    print(f"{Fore.YELLOW}[*] Sprawdzanie działających proxy (wielowątkowo)...{Style.RESET_ALL}")
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_proxy, proxies[:100])
        for res in results:
            if res:
                working_proxies.append(res)
                sys.stdout.write(f"{Fore.GREEN}•{Style.RESET_ALL}")
                sys.stdout.flush()
            if len(working_proxies) >= limit:
                break
    print(f"\n{Fore.GREEN}[+] Znaleziono {len(working_proxies)} szybkich proxy!{Style.RESET_ALL}")
    return working_proxies

# ================= CORE SCRAPER =================

def get_maps_link(name, address):
    """Generuje klikalny link do Google Maps"""
    query = f"{name} {address}"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

def scrape_leads_no_api(keyword, region, limit, proxy=None):
    print(f"\n{Fore.YELLOW}[*] Uruchamiam zaawansowany scraper dla: {keyword} w {region}{Style.RESET_ALL}")
    leads = []
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    # MAGICZNE CIASTECZKO - omija ekran "Zgadzam się" (RODO) na Google. Bez tego skrypt dostaje pustą stronę!
    cookies = {
        "CONSENT": "YES+cb.20230531-04-p0.pl+FX+111"
    }
    
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None

    search_query = f"{keyword} {region}"
    # Zwiększamy bufor w num, by na pewno wyciągnąć limit
    url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}&num={limit + 20}"
    
    try:
        print(f"{Fore.CYAN}[*] Łączenie z bazą Google...{Style.RESET_ALL}")
        response = requests.get(url, headers=headers, cookies=cookies, proxies=proxies, timeout=15)
        
        if response.status_code == 429:
            print(f"{Fore.RED}[!] Google zablokowało IP (Kod 429). Użyj proxy!{Style.RESET_ALL}")
            return leads

        soup = BeautifulSoup(response.text, "html.parser")
        
        # AGRESYWNY PARSER: Szukamy h3 lub divów z klasami odpowiadającymi tytułom w surowym HTML
        for element in soup.find_all(['h3', 'div']):
            if len(leads) >= limit:
                break
                
            # Łapiemy tagi tytułowe lub surowe klasy wyników lokalnych (BNeawe to popularna ukryta klasa w Google)
            if element.name == 'h3' or (element.has_attr('class') and any('BNeawe' in c for c in element['class'])):
                name = element.text.strip()
                
                # Ignorujemy fałszywe bloki typu "Więcej wyników"
                if len(name) < 3 or "Więcej wyników" in name or "http" in name:
                    continue

                # Idziemy w górę drzewa HTML, by chwycić CAŁY kontener biznesu
                parent = element.parent
                for _ in range(4):
                    if parent: parent = parent.parent
                    
                if parent:
                    text_content = parent.get_text(separator=' ')
                    
                    # Regex na polskie numery: +48, spacje, myślniki, kropki
                    phone_match = re.search(r'(?:\+48)?[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}', text_content)
                    
                    if phone_match:
                        phone_raw = phone_match.group()
                        phone_clean = re.sub(r'[^\d+]', '', phone_raw) # Zostawiamy tylko cyfry i +
                        
                        if len(phone_clean) >= 9:
                            # Zapobiegamy dublowaniu leadów w bazie
                            if not any(lead['name'] == name for lead in leads) and not any(lead['phone'] == phone_clean for lead in leads):
                                leads.append({
                                    "name": name,
                                    "address": region,
                                    "phone": phone_clean
                                })
                                
        # Generowanie Smart Linków
        for lead in leads:
            lead['maps_link'] = get_maps_link(lead['name'], lead['address'])
            
        print(f"{Fore.GREEN}[+] Zeskanowano pomyślnie. Znaleziono leadów: {len(leads)}{Style.RESET_ALL}")
        return leads

    except Exception as e:
        print(f"{Fore.RED}[!] Wystąpił błąd podczas scrapowania: {e}{Style.RESET_ALL}")
        return leads

# ================= ZAPIS DANYCH =================

def save_to_phone(data):
    if not data:
        print(f"\n{Fore.RED}[!] Brak danych do zapisania.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.YELLOW}[?] Podaj nazwę pliku (np. leady_fizjo):{Style.RESET_ALL}")
    filename = input(f"{Fore.CYAN}root@monerskiddmax:~# {Style.RESET_ALL}")
    if not filename: filename = "leady_output"
    
    # WYMUSZONA ŚCIEŻKA DO POBRANYCH ANDROIDA
    full_path = f"/sdcard/Download/{filename}.txt"
    
    if not os.path.exists("/sdcard/Download/"):
        full_path = f"{filename}.txt"
        print(f"{Fore.YELLOW}[!] Ścieżka /sdcard/ niedostępna. Zapisuję w obecnym folderze jako {full_path}{Style.RESET_ALL}")
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"=== ZAAWANSOWANE LEADY MONERSKIDDMAX ===\n")
            f.write(f"Wygenerowano: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, item in enumerate(data, 1):
                f.write(f"[{i}] ZNALEZIONY KLIENT:\n")
                f.write(f"💼 Opis Leada: {item['name']} z regionu {item['address']}\n")
                f.write(f"📞 Telefon: {item['phone']}\n")
                f.write(f"📍 Link do Map: {item['maps_link']}\n")
                f.write("-" * 50 + "\n\n")
                
        print(f"\n{Fore.GREEN}[$$$] ZAPISANO PRAWIDŁOWO! Możesz wysyłać!{Style.RESET_ALL}\n{Fore.CYAN}Ścieżka: {full_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Błąd zapisu: {e}{Style.RESET_ALL}")

# ================= MENU GŁÓWNE =================

def main():
    working_proxies = []
    
    while True:
        clear_screen()
        print_banner()
        
        print(f"{Fore.WHITE}Wybierz opcję:{Style.RESET_ALL}")
        print(f"[{Fore.CYAN}1{Style.RESET_ALL}] 🚀 Uruchom Scraper Google Maps (Standardowe IP)")
        print(f"[{Fore.CYAN}2{Style.RESET_ALL}] 🛡️  Zdobądź i sprawdź Proxy (Zalecane)")
        print(f"[{Fore.CYAN}3{Style.RESET_ALL}] 🚀 Uruchom Scraper używając Proxy")
        print(f"[{Fore.CYAN}4{Style.RESET_ALL}] ❌ Wyjdź")
        
        choice = input(f"\n{Fore.YELLOW}[?] Wybór: {Style.RESET_ALL}")
        
        if choice == '1' or choice == '3':
            if choice == '3' and not working_proxies:
                print(f"\n{Fore.RED}[!] Najpierw pobierz proxy (Opcja 2)!{Style.RESET_ALL}")
                time.sleep(2)
                continue
                
            print(f"\n{Fore.YELLOW}[?] Słowo kluczowe (np. hydraulik, mechanik): {Style.RESET_ALL}", end="")
            keyword = input()
            print(f"{Fore.YELLOW}[?] Miasto / Region (np. Warszawa): {Style.RESET_ALL}", end="")
            region = input()
            print(f"{Fore.YELLOW}[?] Max ilość leadów do przeszukania: {Style.RESET_ALL}", end="")
            try:
                limit = int(input())
            except:
                limit = 10
            
            selected_proxy = None
            if choice == '3':
                selected_proxy = random.choice(working_proxies)
                print(f"{Fore.CYAN}[*] Używam proxy: {selected_proxy}{Style.RESET_ALL}")
                
            leads = scrape_leads_no_api(keyword, region, limit, proxy=selected_proxy)
            
            if leads:
                save_to_phone(leads)
            else:
                print(f"\n{Fore.RED}[!] Nie znaleziono leadów. Sprawdź dokładnie zapytanie lub użyj proxy (Google blokuje czyste połączenia HTTP w niektórych sieciach).{Style.RESET_ALL}")
            
            input(f"\n{Fore.WHITE}Wciśnij ENTER, aby wrócić do menu...{Style.RESET_ALL}")
            
        elif choice == '2':
            raw_proxies = get_free_proxies()
            if raw_proxies:
                working_proxies = check_and_filter_proxies(raw_proxies)
            input(f"\n{Fore.WHITE}Wciśnij ENTER, aby wrócić do menu...{Style.RESET_ALL}")
            
        elif choice == '4':
            print(f"\n{Fore.GREEN}[*] Pozdro mordo, owocnych łowów na leady!{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Przerwano przez użytkownika. Elo!{Style.RESET_ALL}")
        sys.exit(0)
        
