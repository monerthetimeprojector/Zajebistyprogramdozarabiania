import os
import time
import random
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from colorama import init, Fore, Style

# Inicjalizacja kolorów - Lean Skid Vibe
init(autoreset=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
]

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    lean_color = Fore.MAGENTA + Style.BRIGHT
    white = Fore.WHITE + Style.BRIGHT
    
    banner = f"""{lean_color}
  __  __                       _____ _    _     _     _                     
 |  \/  |                     / ____| |  (_)   | |   | |                    
 | \  / | ___  _ __   ___ _ _| (___ | | ___  __| | __| |_ __ ___   __ ___  __
 | |\/| |/ _ \| '_ \ / _ \ '__\___ \| |/ / |/ _` |/ _` | '_ ` _ \ / _` \ \/ /
 | |  | | (_) | | | |  __/ |  ____) |   <| | (_| | (_| | | | | | | (_| |>  < 
 |_|  |_|\___/|_| |_|\___|_| |_____/|_|\_\_|\__,_|\__,_|_| |_| |_|\__,_/_/\_\\
    """
    print(banner)
    print(f"{white}                  Credits: @monerthetimeprojector on github")
    print(f"{white}                               All rights reserved\n")

def get_voivodeships():
    return [
        "Cała Polska", "Dolnośląskie", "Kujawsko-pomorskie", "Lubelskie", 
        "Lubuskie", "Łódzkie", "Małopolskie", "Mazowieckie", "Opolskie", 
        "Podkarpackie", "Podlaskie", "Pomorskie", "Śląskie", "Świętokrzyskie", 
        "Warmińsko-mazurskie", "Wielkopolskie", "Zachodniopomorskie"
    ]

def scrape_proxies():
    print(f"\n{Fore.CYAN}[*] Pobieranie darmowych proxy z sieci (Proxy Scraper)...")
    proxies = []
    try:
        res = requests.get('https://free-proxy-list.net/', timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table', class_='table table-striped table-bordered')
        for row in table.tbody.find_all('tr'):
            cols = row.find_all('td')
            if cols[6].text == 'yes': # Tylko HTTPS
                proxies.append(f"{cols[0].text}:{cols[1].text}")
        print(f"{Fore.GREEN}[+] Znaleziono {len(proxies)} potencjalnych proxy HTTPS.")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}[!] Błąd pobierania proxy: {e}")
        return []

def check_proxy(proxy):
    proxies_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    try:
        res = requests.get("https://www.google.com/search?q=test", proxies=proxies_dict, timeout=4)
        if res.status_code == 200:
            return proxy
    except:
        pass
    return None

def verify_proxies(proxies):
    print(f"{Fore.CYAN}[*] Weryfikacja proxy z Google Maps (Proxy Checker)...")
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_proxy, proxies)
        for proxy in results:
            if proxy:
                working_proxies.append(proxy)
                print(f"{Fore.GREEN}[+] Działające proxy: {proxy}")
    
    print(f"\n{Fore.MAGENTA}[!] Pomyślnie zweryfikowano {len(working_proxies)} proxy.{Style.RESET_ALL}")
    return working_proxies

def scrape_google_leads(keyword, location, max_results, working_proxies):
    print(f"\n{Fore.CYAN}[*] Inicjalizacja silnika G-Maps Scraper...")
    time.sleep(1)
    
    query = f"{keyword} {location}".replace(" ", "+")
    valid_leads = []
    page = 0
    
    while len(valid_leads) < max_results:
        current_proxy = random.choice(working_proxies) if working_proxies else None
        proxies_dict = {"http": f"http://{current_proxy}", "https": f"http://{current_proxy}"} if current_proxy else None
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        # Ciasteczko RODO - kluczowe dla uniknięcia blokad w Europie
        cookies = {"CONSENT": "YES+cb.20230101-08-p0.pl+FX+414"}
        
        url = f"https://www.google.com/search?q={query}&tbm=lcl&start={page * 10}"
        
        try:
            print(f"{Fore.YELLOW}[~] Wysyłanie zapytania (Strona {page+1}) | Proxy: {current_proxy or 'BRAK'}")
            
            # Timeout (5s na połączenie, 10s na dane) - zapobiega wieszaniu się skryptu
            res = requests.get(url, headers=headers, cookies=cookies, proxies=proxies_dict, timeout=(5, 10))
            
            if res.status_code == 429:
                print(f"{Fore.RED}[!] Google wykryło bota (429). Rotacja...")
                if current_proxy in working_proxies:
                    working_proxies.remove(current_proxy)
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            businesses = soup.find_all('div', class_='g')
            
            if not businesses:
                print(f"{Fore.RED}[!] Brak wyników na tej stronie. Przerywam pętlę.")
                break

            for biz in businesses:
                if len(valid_leads) >= max_results:
                    break
                    
                name_tag = biz.find('h3')
                if not name_tag:
                    continue
                name = name_tag.text
                
                links = biz.find_all('a', href=True)
                has_website = any("Witryna" in a.text or "Strona" in a.text or "Website" in a.text for a in links)
                
                if not has_website:
                    valid_leads.append({"Nazwa": name, "Wyszukiwanie": query.replace("+", " ")})
                    print(f"{Fore.GREEN}[+] Złowiono: {name} (BRAK STRONY WWW)")
            
            page += 1
            time.sleep(random.uniform(2.0, 5.0)) # Delay dla bezpieczeństwa
            
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}[!] Timeout: Google zablokowało połączenie.")
            if current_proxy in working_proxies:
                working_proxies.remove(current_proxy)
            else:
                break
        except Exception as e:
            print(f"{Fore.RED}[!] Błąd: {e}")
            if current_proxy in working_proxies:
                working_proxies.remove(current_proxy)
                
    return valid_leads

def main():
    clear_screen()
    print_banner()
    
    working_proxies = []
    
    print(f"{Fore.GREEN}[?] Czy chcesz użyć zintegrowanego Proxy Scrapera? (y/n)")
    use_proxy = input(f"{Fore.MAGENTA}MonerSkiddmax > {Fore.WHITE}").lower()
    
    if use_proxy == 'y':
        raw_proxies = scrape_proxies()
        if raw_proxies:
            working_proxies = verify_proxies(raw_proxies)
        if not working_proxies:
            print(f"{Fore.YELLOW}[!] Brak działających proxy. Kontynuuję na własnym IP.")
    
    print(f"\n{Fore.GREEN}[?] Wybierz obszar do scrapowania:")
    voivodeships = get_voivodeships()
    for i, v in enumerate(voivodeships):
        print(f"{Fore.GREEN}[{i}] {Fore.WHITE}{v}")
    
    try:
        v_choice = int(input(f"\n{Fore.MAGENTA}MonerSkiddmax > {Fore.WHITE}"))
        selected_location = voivodeships[v_choice]
    except (ValueError, IndexError):
        selected_location = "Cała Polska"

    print(f"\n{Fore.GREEN}[?] Wpisz słowo kluczowe:")
    keyword = input(f"{Fore.MAGENTA}MonerSkiddmax > {Fore.WHITE}")

    print(f"\n{Fore.GREEN}[?] Ile leadów BEZ STRONY WWW:")
    try:
        max_results = int(input(f"{Fore.MAGENTA}MonerSkiddmax > {Fore.WHITE}"))
    except ValueError:
        max_results = 20

    print(f"\n{Fore.GREEN}[?] Nazwa pliku:")
    filename = input(f"{Fore.MAGENTA}MonerSkiddmax > {Fore.WHITE}")
    if not filename: filename = "scraped_leads"

    results = scrape_google_leads(keyword, selected_location, max_results, working_proxies)
    
    if not results:
        print(f"\n{Fore.RED}[!] Brak wyników. Zmień IP (tryb samolotowy) lub użyj proxy.")
        return

    save_dir = os.path.expanduser("~/storage/shared/Download")
    if not os.path.exists(save_dir): save_dir = os.getcwd()

    full_path = os.path.join(save_dir, f"{filename}.txt")
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"--- MONERSKIDDMAX LEAD GEN ---\n")
            f.write(f"Kategoria: {keyword.upper()} | Lokacja: {selected_location.upper()}\n")
            f.write("Status: WYZNACZENI DO STWORZENIA STRONY WWW\n\n")
            for idx, r in enumerate(results, 1):
                f.write(f"{idx}. {r['Nazwa']}\n   [BRAK PODPIĘTEJ STRONY]\n\n")
        print(f"{Fore.GREEN}[+] Zapisano! Plik: {full_path}")
    except Exception as e:
        print(f"{Fore.RED}[!] Błąd zapisu: {e}")

    print(f"\n{Fore.MAGENTA}MonerSkiddmax out. Pzdrr okt.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
            
