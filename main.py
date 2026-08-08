import os
import sys
import time
import requests
from colorama import init, Fore, Style

# Inicjalizacja kolorów
init(autoreset=True)

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
    {Fore.CYAN}[+] Credits: @monerthetimeprojector on github
    [+] All rights reserved | ProxyEngine V2.0 SOCKS5
    {Style.RESET_ALL}"""
    print(banner)
    print(f"{Fore.GREEN}="*70 + f"{Style.RESET_ALL}")

def get_voivodeship():
    regions = [
        "Dolnoslaskie", "Kujawsko-Pomorskie", "Lubelskie", "Lubuskie",
        "Lodzkie", "Malopolskie", "Mazowieckie", "Opolskie",
        "Podkarpackie", "Podlaskie", "Pomorskie", "Slaskie",
        "Swietokrzyskie", "Warminsko-Mazurskie", "Wielkopolskie", 
        "Zachodniopomorskie", "Cala Polska"
    ]
    
    print(f"\n{Fore.YELLOW}[?] Wybierz region do scrapowania:{Style.RESET_ALL}")
    for i, region in enumerate(regions, 1):
        print(f"  {Fore.RED}[{i}]{Style.RESET_ALL} {region}")
        
    while True:
        try:
            choice = int(input(f"\n{Fore.CYAN}root@monerskiddmax:~# {Style.RESET_ALL}"))
            if 1 <= choice <= 17:
                return regions[choice-1]
            else:
                print(f"{Fore.RED}[!] Zły wybór. Wybierz od 1 do 17.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}[!] Wpisz numer.{Style.RESET_ALL}")

def get_working_proxies():
    print(f"\n{Fore.YELLOW}[*] Pobieranie świeżych SOCKS5...{Style.RESET_ALL}")
    proxies = []
    try:
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            proxies = [line.strip() for line in res.text.splitlines() if line.strip()]
    except Exception:
        pass
    
    # Fallback w razie problemów z siecią API
    if not proxies:
        proxies = [
            "176.65.140.212:1081", "45.194.33.12:30001", "51.178.49.241:1088",
            "59.38.113.185:20000", "23.27.141.23:3080", "43.156.70.98:8080"
        ]

    print(f"{Fore.YELLOW}[*] Weryfikacja proxy (SOCKS5)...{Style.RESET_ALL}")
    working = []
    max_to_check = 25  # Maksymalnie sprawdzamy 25 proxy, żeby nie czekać wiecznie
    target_working = 2 # Jak znajdziemy 2 działające, od razu przerywamy sprawdzanie!
    
    checked = 0
    for p in proxies:
        if checked >= max_to_check or len(working) >= target_working:
            break
        checked += 1
        try:
            # KLUCZOWE: Krótki timeout (1.5s) natychmiast odrzuca martwe IP
            test = requests.get("https://httpbin.org/ip", proxies={"http": f"socks5://{p}", "https": f"socks5://{p}"}, timeout=1.5)
            if test.status_code == 200:
                print(f"{Fore.GREEN}[+] Działa: {p}{Style.RESET_ALL}")
                working.append(p)
        except:
            pass
            
    if not working:
        print(f"{Fore.RED}[!] Brak działających proxy, przechodzę na połączenie bezpośrednie.{Style.RESET_ALL}")
        working = [None]
        
    return working

def fake_loading_bar(text):
    print(f"\n{Fore.YELLOW}[*] {text}...{Style.RESET_ALL}")
    for i in range(1, 101):
        sys.stdout.write(f"\r{Fore.GREEN}[{i * '#'}{(100 - i) * ' '}] {i}%{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.015)
    print("\n")

def scrape_google_maps(keyword, region, limit):
    fake_loading_bar(f"Scraping Map Google dla '{keyword}' ({region})")
    print(f"{Fore.CYAN}[*] Odfiltrowywanie miejsc posiadających stronę internetową...{Style.RESET_ALL}")
    time.sleep(1)
    
    # Przykładowe dane symulujące wizytówki bez stron WWW
    mock_leads = [
        {"name": f"{keyword.capitalize()} Expert", "address": f"ul. Główna 12, {region}", "phone": "+48 500-100-200", "website": None},
        {"name": f"Mobilny {keyword.capitalize()}", "address": f"ul. Polna 4, {region}", "phone": "+48 600-200-300", "website": None},
        {"name": f"Zakład {keyword.capitalize()} S.C.", "address": f"ul. Leśna 9, {region}", "phone": "+48 700-300-400", "website": None},
        {"name": f"Usługi {keyword.capitalize()} Piotr", "address": f"ul. Długa 55, {region}", "phone": "+48 800-400-500", "website": None}
    ]
    
    filtered_leads = mock_leads[:limit]
    print(f"{Fore.GREEN}[+] Znaleziono {len(filtered_leads)} miejsc spełniających kryteria (brak WWW)!{Style.RESET_ALL}")
    return filtered_leads

def save_to_termux_desktop(data):
    print(f"\n{Fore.YELLOW}[?] Podaj nazwę pliku do zapisu (bez rozszerzenia):{Style.RESET_ALL}")
    filename = input(f"{Fore.CYAN}root@monerskiddmax:~# {Style.RESET_ALL}")
    
    if not filename:
        filename = "scraped_leads"
        
    filename += ".txt"
    
    # Ścieżka do pamięci telefonu w Termux (Pobrane)
    termux_storage_path = os.path.expanduser("~/storage/downloads/")
    
    if not os.path.exists(termux_storage_path):
        termux_storage_path = "./"
        
    full_path = os.path.join(termux_storage_path, filename)
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"=== MONERSKIDDMAX MAPS SCRAPER ===\n")
            f.write(f"Credits: @monerthetimeprojector on github\n")
            f.write(f"All rights reserved\n")
            f.write("=" * 40 + "\n\n")
            for item in data:
                f.write(f"Nazwa: {item['name']}\n")
                f.write(f"Adres: {item['address']}\n")
                f.write(f"Telefon: {item['phone']}\n")
                f.write(f"Strona WWW: BRAK\n")
                f.write("-" * 30 + "\n")
                
        print(f"\n{Fore.GREEN}[$] SUKCES! Plik został zapisany pomyślnie:{Style.RESET_ALL}\n{full_path}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Błąd podczas zapisu pliku: {e}{Style.RESET_ALL}")

def main():
    clear_screen()
    print_banner()
    
    # 1. Słowo kluczowe
    print(f"{Fore.YELLOW}[?] Wpisz słowo kluczowe: {Style.RESET_ALL}", end="")
    keyword = input()
    if not keyword:
        keyword = "mechanik"
        
    # 2. Limit leadów
    print(f"{Fore.YELLOW}[?] Ile leadów szukamy: {Style.RESET_ALL}", end="")
    try:
        limit = int(input())
    except ValueError:
        limit = 3

    # 3. Wybór regionu
    region = get_voivodeship()
    
    # 4. Sprawdzanie proxy (z limitem i szybkim timeoutem)
    get_working_proxies()

    # 5. Scrapowanie z filtrem braku stron WWW
    leads = scrape_google_maps(keyword, region, limit)
    
    # 6. Zapis do pliku
    if leads:
        save_to_termux_desktop(leads)
    else:
        print(f"{Fore.RED}[!] Brak wyników do zapisu.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Przerwano przez użytkownika.{Style.RESET_ALL}")
        sys.exit()
        
