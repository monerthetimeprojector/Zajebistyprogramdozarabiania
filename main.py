import os
import requests
import random
import urllib.parse
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
import concurrent.futures

init(autoreset=True)

def print_banner():
    print(f"{Fore.MAGENTA}MonerSkiddmax v2.6 - [Proxy, Checker & Searcher Active]{Style.RESET_ALL}")

def check_proxy(proxy):
    try:
        response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        return proxy if response.status_code == 200 else None
    except:
        return None

def get_free_proxies():
    try:
        response = requests.get("https://free-proxy-list.net/", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        proxies = []
        for row in soup.find('tbody').find_all('tr')[:20]:
            cols = row.find_all('td')
            proxies.append(f"http://{cols[0].text}:{cols[1].text}")
        return proxies
    except:
        return []

def search_leads(keyword, limit, working_proxies):
    print(f"{Fore.CYAN}[*] Wyszukiwanie leadów dla: {keyword}...{Style.RESET_ALL}")
    results = []
    
    # Wybieramy losowe działające proxy
    proxy = {"http": random.choice(working_proxies), "https": random.choice(working_proxies)}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
    
    query = urllib.parse.quote(keyword)
    url = f"https://www.google.com/search?q={query}+firmy+mapy"
    
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for g in soup.find_all('h3')[:limit]:
            name = g.text
            if "..." in name: continue
            maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name)}"
            results.append({"name": name, "link": maps_link})
    except Exception as e:
        print(f"{Fore.RED}[!] Błąd w trakcie wyszukiwania: {e}{Style.RESET_ALL}")
    
    return results

def main():
    os.system('clear')
    print_banner()
    
    # 1. Ładowanie proxy
    if not os.path.exists('proxies.txt'):
        raw_proxies = get_free_proxies()
    else:
        with open('proxies.txt', 'r') as f:
            raw_proxies = [l.strip() for l in f if l.strip()]

    # 2. Sprawdzanie proxy
    print(f"{Fore.CYAN}[*] Sprawdzam proxy...{Style.RESET_ALL}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        working_proxies = [p for p in executor.map(check_proxy, raw_proxies) if p]
    
    if not working_proxies:
        print(f"{Fore.RED}[!] Brak działających proxy. Program kończy działanie.{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}[+] Działa {len(working_proxies)} proxy.{Style.RESET_ALL}")
    
    # 3. Wyszukiwanie
    keyword = input(f"{Fore.YELLOW}[?] Słowo kluczowe: {Style.RESET_ALL}")
    limit = int(input(f"{Fore.YELLOW}[?] Ile leadów: {Style.RESET_ALL}"))
    
    leads = search_leads(keyword, limit, working_proxies)
    
    if leads:
        filename = input(f"{Fore.YELLOW}[?] Nazwa pliku wyjściowego: {Style.RESET_ALL}")
        path = f"/sdcard/Download/{filename}.txt"
        with open(path, "w", encoding="utf-8") as f:
            for item in leads:
                f.write(f"Firma: {item['name']}\nLink: {item['link']}\n---\n")
        print(f"{Fore.GREEN}[+] Zapisano: {path}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[!] Nic nie znaleziono.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
    
