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

# Lista User-Agentów do rotacji, by wyglądać jak różne przeglądarki
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
    {Fore.CYAN}[+] Wersja: v2.2 AUTO-ROTATION TANK
    [+] Credits: @monerthetimeprojector 
    [+] Ulepszone: Auto-Rotacja Proxy w locie, Detekcja Bana 429
    {Style.RESET_ALL}"""
    print(banner)

# ================= PROXY SYSTEM =================

def get_free_proxies():
    print(f"\n{Fore.YELLOW}[*] Pobieranie darmowych proxy (HTTP/S)...{Style.RESET_ALL}")
    try:
        # Pobieramy z potężnego API proxyscrape
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        response = requests.get(url, timeout=10)
        proxies = response.text.strip().split("\r\n")
        proxies = [p for p in proxies if p]
        print(f"{Fore.GREEN}[+] Pociągnięto {len(proxies)} proxy z bazy.{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}[!] Błąd pobierania proxy: {e}{Style.RESET_ALL}")
        return []

def check_proxy(proxy):
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        # NOWOŚĆ: Sprawdzamy nie tylko czy jest połączenie, ale czy Google daje 200 OK (brak bana)!
        res = requests.get("https://www.google.com/search?q=test", proxies=proxies, headers=headers, timeout=5)
        if res.status_code == 200:
            return proxy
        return None
    except:
        return None

def check_and_filter_proxies(proxies, limit=20):
    print(f"{Fore.YELLOW}[*] Ostre filtrowanie proxy (szukam tych bez bana 429 od Google)...{Style.RESET_ALL}")
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        # Sprawdzamy pierwsze 250, żeby znaleźć perełki
        results = executor.map(check_proxy, proxies[:250])
        for res in results:
            if res:
                working_proxies.append(res)
                sys.stdout.write(f"{Fore.GREEN}•{Style.RESET_ALL}")
                sys.stdout.flush()
            if len(working_proxies) >= limit:
                break
    print(f"\n{Fore.GREEN}[+] Przefiltrowano! Masz {len(working_proxies)} potężnych proxy, gotowych do akcji.{Style.RESET_ALL}")
    return working_proxies

# ================= CORE SCRAPER =================

def get_maps_link(name, address):
    query = f"{name} {address}"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

def scrape_leads_no_api(keyword, region, limit, working_proxies=None):
    print(f"\n{Fore.YELLOW}[*] Uruchamiam zmasowany atak dla: {keyword} w {region}{Style.RESET_ALL}")
    leads = []
    
    cookies = {"CONSENT": "YES+cb.20230531-04-p0.pl+FX+111"}
    
    # Dodane hl=pl, aby Google dawało polskie mapy
    search_query = f"{keyword} {region}"
    url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}&num={limit + 20}&hl=pl"
    
    max_retries = 5
    attempts = 0
    
    # Pętla auto-rotacji - jak jedno proxy padnie, skrypt bierze następne!
    while attempts < max_retries:
        attempts += 1
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8",
            "Referer": "https://www.google.com/"
        }
        
        current_proxy = None
        proxies_dict = None
        
        if working_proxies:
            if not working_proxies:
                print(f"{Fore.RED}[!] Skończyły się działające proxy. Przerywam...{Style.RESET_ALL}")
                break
            current_proxy = random.choice(working_proxies)
            proxies_dict = {"http": f"http://{current_proxy}", "https": f"http://{current_proxy}"}
            print(f"{Fore.CYAN}[*] [Próba {attempts}/{max_retries}] Lecę przez IP: {current_proxy}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}[*] [Próba {attempts}/{max_retries}] Łączenie z bazą Google (bez proxy)...{Style.RESET_ALL}")
            
        try:
            response = requests.get(url, headers=headers, cookies=cookies, proxies=proxies_dict, timeout=15)
            
            # Detekcja Bana 429
            if response.status_code == 429:
                print(f"{Fore.RED}[!] Błąd 429! To IP ma limit.{Style.RESET_ALL}")
                if working_proxies and current_proxy in working_proxies:
                    working_proxies.remove(current_proxy) # Wywalamy zepsute proxy
                    print(f"{Fore.YELLOW}[*] Wywalam zbanowane proxy. Podmieniam na nowe...{Style.RESET_ALL}")
                time.sleep(2)
                continue # Pętla startuje od nowa z nowym proxy!
                
            elif response.status_code != 200:
                print(f"{Fore.RED}[!] Inny błąd: {response.status_code}. Próbuję dalej...{Style.RESET_ALL}")
                continue

            # Jeśli doszliśmy tutaj, mamy kod 200 OK! Scrapujemy.
            print(f"{Fore.GREEN}[+] Kod 200! Mam HTML. Rozpoczynam cięcie danych...{Style.RESET_ALL}")
            soup = BeautifulSoup(response.text, "html.parser")
            
            for element in soup.find_all(['h3', 'div']):
                if len(leads) >= limit:
                    break
                    
                if element.name == 'h3' or (element.has_attr('class') and any('BNeawe' in c for c in element['class'])):
                    name = element.text.strip()
                    
                    if len(name) < 3 or "Więcej wyników" in name or "http" in name:
                        continue

                    parent = element.parent
                    for _ in range(4):
                        if parent: parent = parent.parent
                        
                    if parent:
                        text_content = parent.get_text(separator=' ')
                        phone_match = re.search(r'(?:\+48)?[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}', text_content)
                        
                        if phone_match:
                            phone_raw = phone_match.group()
                            phone_clean = re.sub(r'[^\d+]', '', phone_raw)
                            
                            if len(phone_clean) >= 9:
                                if not any(lead['name'] == name for lead in leads) and not any(lead['phone'] == phone_clean for lead in leads):
                                    leads.append({
                                        "name": name,
                                        "address": region,
                                        "phone": phone_clean
                                    })
                                    
            # Zakończ pętlę prób, bo udało się pobrać HTML i go przetworzyć
            break 
            
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}[!] Błąd połączenia: {e}{Style.RESET_ALL}")
            if working_proxies and current_proxy in working_proxies:
                working_proxies.remove(current_proxy)
            time.sleep(2)
            continue
            
    # Na koniec dodajemy linki
    for lead in leads:
        lead['maps_link'] = get_maps_link(lead['name'], lead['address'])
        
    print(f"\n{Fore.GREEN}[$$$] Zakończono skanowanie. Upolowano leadów: {len(leads)}{Style.RESET_ALL}")
    return leads

# ================= ZAPIS DANYCH =================

def save_to_phone(data):
    if not data:
        print(f"\n{Fore.RED}[!] Brak danych do zapisania. Zmień frazę lub odśwież listę proxy.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.YELLOW}[?] Podaj nazwę pliku (np. leady_mechanik):{Style.RESET_ALL}")
    filename = input(f"{Fore.CYAN}root@monerskiddmax:~# {Style.RESET_ALL}")
    if not filename: filename = "leady_output"
    
    full_path = f"/sdcard/Download/{filename}.txt"
    
    if not os.path.exists("/sdcard/Download/"):
        full_path = f"{filename}.txt"
    
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
                
        print(f"\n{Fore.GREEN}[$$$] ZAPISANO PRAWIDŁOWO! Możesz wgrywać do bazy!{Style.RESET_ALL}\n{Fore.CYAN}Plik: {full_path}{Style.RESET_ALL}")
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
        print(f"[{Fore.CYAN}2{Style.RESET_ALL}] 🛡️  Zdobądź i sprawdź Proxy (Rygorystyczny skan)")
        print(f"[{Fore.CYAN}3{Style.RESET_ALL}] 🚀 Uruchom Scraper używając Proxy (Auto-Rotacja)")
        print(f"[{Fore.CYAN}4{Style.RESET_ALL}] ❌ Wyjdź")
        
        if working_proxies:
            print(f"\n{Fore.GREEN}[*] Aktywne proxy w pamięci: {len(working_proxies)}{Style.RESET_ALL}")
            
        choice = input(f"\n{Fore.YELLOW}[?] Wybór: {Style.RESET_ALL}")
        
        if choice == '1' or choice == '3':
            if choice == '3' and not working_proxies:
                print(f"\n{Fore.RED}[!] Mordzia, nie masz żadnych sprawdzonych proxy w pamięci! Odpal najpierw Opcję 2.{Style.RESET_ALL}")
                time.sleep(3)
                continue
                
            print(f"\n{Fore.YELLOW}[?] Słowo kluczowe (np. hydraulik, mechanik, fryzjer): {Style.RESET_ALL}", end="")
            keyword = input()
            print(f"{Fore.YELLOW}[?] Miasto / Region (np. Warszawa): {Style.RESET_ALL}", end="")
            region = input()
            print(f"{Fore.YELLOW}[?] Max ilość leadów do przeszukania: {Style.RESET_ALL}", end="")
            try:
                limit = int(input())
            except:
                limit = 10
            
            # Przekazujemy listę proxy (jeśli wybrano 3) albo None (jeśli 1)
            proxies_to_use = working_proxies.copy() if choice == '3' else None
            
            leads = scrape_leads_no_api(keyword, region, limit, proxies_to_use)
            
            if leads:
                save_to_phone(leads)
            
            input(f"\n{Fore.WHITE}Wciśnij ENTER, aby wrócić do menu...{Style.RESET_ALL}")
            
        elif choice == '2':
            raw_proxies = get_free_proxies()
            if raw_proxies:
                # Ogranicznik można zdjąć w kodzie wyżej, jak chcesz skanować tysiące na raz
                working_proxies = check_and_filter_proxies(raw_proxies, limit=15)
            input(f"\n{Fore.WHITE}Wciśnij ENTER, aby wrócić do menu...{Style.RESET_ALL}")
            
        elif choice == '4':
            print(f"\n{Fore.GREEN}[*] Z fartem mordo, niech leady wchodzą szeroko!{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Twarde lądowanie. Zamykam apkę. Elo!{Style.RESET_ALL}")
        sys.exit(0)
            
