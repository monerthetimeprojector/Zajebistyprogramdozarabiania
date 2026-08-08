import os
import requests
import random
import urllib.parse
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
import concurrent.futures

init(autoreset=True)

def print_banner():
    print(f"{Fore.MAGENTA}MonerSkiddmax v2.5 - [Auto-Proxy & Checker Enabled]{Style.RESET_ALL}")

# 1. AUTO-CHECKER: sprawdza czy proxy działa
def check_proxy(proxy):
    try:
        response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        return proxy if response.status_code == 200 else None
    except:
        return None

# 2. AUTO-SEARCHER: szuka darmowych proxy (uproszczone)
def get_free_proxies():
    print(f"{Fore.CYAN}[*] Szukam darmowych proxy...{Style.RESET_ALL}")
    try:
        url = "https://free-proxy-list.net/"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        proxies = []
        for row in soup.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            proxies.append(f"http://{cols[0].text}:{cols[1].text}")
        return proxies[:20] # Bierzemy 20 najnowszych
    except:
        return []

def main():
    os.system('clear')
    print_banner()
    
    # Wczytywanie z pliku lub szukanie nowych
    if not os.path.exists('proxies.txt'):
        print(f"{Fore.YELLOW}[!] Brak proxies.txt. Uruchamiam auto-searcher...{Style.RESET_ALL}")
        raw_proxies = get_free_proxies()
    else:
        with open('proxies.txt', 'r') as f:
            raw_proxies = [l.strip() for l in f if l.strip()]

    # Automatyczne sprawdzanie (CHECKER)
    print(f"{Fore.CYAN}[*] Sprawdzam {len(raw_proxies)} proxy (to może zająć chwilę)...{Style.RESET_ALL}")
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_proxy, raw_proxies))
        working_proxies = [p for p in results if p]
    
    print(f"{Fore.GREEN}[+] Działa {len(working_proxies)} proxy.{Style.RESET_ALL}")
    
    if not working_proxies:
        print(f"{Fore.RED}[!] Brak działających proxy!{Style.RESET_ALL}")
        return

    # Reszta logiki wyszukiwania
    keyword = input(f"{Fore.YELLOW}[?] Słowo kluczowe: {Style.RESET_ALL}")
    limit = int(input(f"{Fore.YELLOW}[?] Ile leadów: {Style.RESET_ALL}"))
    
    # ... (kod wyszukiwania z poprzedniej wersji z użyciem working_proxies)
    # Wykorzystaj tutaj working_proxies = random.choice(working_proxies) przy zapytaniu
    
    print(f"{Fore.GREEN}[$] Gotowe do pracy z {len(working_proxies)} aktywnymi proxy.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
    
