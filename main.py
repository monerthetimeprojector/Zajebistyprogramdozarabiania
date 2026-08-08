import requests
import random
import time
import sys
from bs4 import BeautifulSoup
from colorama import Fore, init

# Init
init(autoreset=True)

# CONFIG
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def banner():
    print(f"{Fore.MAGENTA}  __  __  ____   _   _  ____  ____  ____  ____  _  _  ____  ____  _  _  ____ ")
    print(f"{Fore.MAGENTA} (  \/  )(  _ \ ( )_( )(  __)(  _ \(  _ \(  __)( )/ )(  _ \(  _ \( )/ )(  _ \")
    print(f"{Fore.MAGENTA}  )    (  ) _ <  ) _ (  ) _)  )   / )   / ) _)  )  (  )(_) ))   / )  (  )(_) )")
    print(f"{Fore.MAGENTA} (__/\/\_)(____/ (_) (_)(____)(__\_)(__\_)(____)(_)\_)(____/(__\_)(_)\_)(____/")
    print(f"{Fore.WHITE} Credits: @monerthetimeprojector | ProxyEngine V2.0 SOCKS5\n")

# --- PROXY ENGINE ---
def get_fresh_proxies():
    print(f"{Fore.CYAN}[*] Pobieranie 100 świeżych SOCKS5...")
    url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all&ssl=all&anonymity=all"
    try:
        res = requests.get(url, timeout=15)
        return res.text.strip().split('\r\n')
    except:
        return []

def is_proxy_working(proxy):
    proxies = {"http": f"socks5://{proxy}", "https": f"socks5://{proxy}"}
    try:
        # Szybki ping do google
        requests.get("https://www.google.com", proxies=proxies, timeout=3)
        return True
    except:
        return False

# --- MAIN SCRAPER ---
def run_scraper():
    banner()
    
    # SETUP
    keyword = input(f"{Fore.YELLOW}[?] Wpisz słowo kluczowe: ")
    loc = "Polska" # Możesz dodać input, jeśli chcesz
    target_count = int(input(f"{Fore.YELLOW}[?] Ile leadów szukamy: "))
    
    # Initialize Pool
    raw_proxies = get_fresh_proxies()
    valid_proxies = []
    
    print(f"{Fore.CYAN}[*] Weryfikacja proxy (SOCKS5)...")
    for p in raw_proxies:
        if len(valid_proxies) >= 100: break
        if is_proxy_working(p):
            valid_proxies.append(p)
            print(f"{Fore.GREEN}[+] Działa: {p}")
            
    if not valid_proxies:
        print(f"{Fore.RED}[!] Nie znaleziono działających proxy. Zrestartuj.")
        sys.exit()

    # SCRAPING LOOP
    leads = []
    page = 0
    
    while len(leads) < target_count:
        if not valid_proxies:
            print(f"{Fore.RED}[!] Pula proxy pusta! Pobieram nową...")
            valid_proxies = get_fresh_proxies()
            continue
            
        proxy = random.choice(valid_proxies)
        proxies = {"http": f"socks5://{proxy}", "https": f"socks5://{proxy}"}
        
        try:
            print(f"{Fore.YELLOW}[~] Zapytanie | Proxy: {proxy} | Strona: {page+1}")
            
            # Wymuszenie prostego HTML
            url = f"https://www.google.com/search?q={keyword}+{loc}&tbm=lcl&gbv=1&start={page * 10}"
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            
            res = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            
            if res.status_code != 200:
                raise Exception("Bad Status Code")
                
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Parsing - szukamy klas map
            items = soup.find_all('div', class_='VkpGBb')
            
            if not items:
                print(f"{Fore.RED}[!] Brak wyników (może być CAPTCHA lub brak danych).")
                valid_proxies.remove(proxy) # Proxy padło
                continue
            
            for item in items:
                if len(leads) >= target_count: break
                
                # Ekstrakcja nazwy
                name_tag = item.find('div', class_='rllt__details')
                if name_tag:
                    name = name_tag.text.split('·')[0].strip()
                    if name not in leads:
                        leads.append(name)
                        print(f"{Fore.GREEN}[+] Złowiono: {name}")
            
            page += 1
            time.sleep(random.uniform(2, 4)) # Anti-ban delay
            
        except Exception as e:
            print(f"{Fore.RED}[!] Błąd zapytania: {e}. Switching proxy...")
            if proxy in valid_proxies:
                valid_proxies.remove(proxy)
            continue
            
    print(f"{Fore.CYAN}\n[!] Sukces! Znaleziono {len(leads)} leadów.")

if __name__ == "__main__":
    run_scraper()
    
