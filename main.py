import os
import sys
import time
import requests
import urllib.parse
from colorama import init, Fore, Style

# Inicjalizacja
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
    [+] All rights reserved | LinkGen v1.0
    {Style.RESET_ALL}"""
    print(banner)

def get_maps_link(name, address):
    """Generuje klikalny link do Google Maps"""
    query = f"{name} {address}"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

def scrape_google_maps(keyword, region, limit):
    # Symulacja danych
    mock_leads = [
        {"name": f"{keyword.capitalize()} Expert", "address": f"Olsztyn", "phone": "+48 500-100-200"},
        {"name": f"Mobilny {keyword.capitalize()}", "address": f"Lidzbark Warmiński", "phone": "+48 600-200-300"},
    ]
    
    # Dodajemy linki do każdego obiektu
    for lead in mock_leads:
        lead['maps_link'] = get_maps_link(lead['name'], lead['address'])
        
    return mock_leads[:limit]

def save_to_phone(data):
    print(f"\n{Fore.YELLOW}[?] Podaj nazwę pliku (np. leady_fizjo):{Style.RESET_ALL}")
    filename = input(f"{Fore.CYAN}root@monerskiddmax:~# {Style.RESET_ALL}")
    if not filename: filename = "leady_output"
    
    # WYMUSZONA ŚCIEŻKA DO POBRANYCH ANDROIDA
    full_path = f"/sdcard/Download/{filename}.txt"
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"=== MONERSKIDDMAX LEADS ===\n\n")
            for item in data:
                f.write(f"Nazwa: {item['name']}\n")
                f.write(f"Adres: {item['address']}\n")
                f.write(f"Telefon: {item['phone']}\n")
                f.write(f"Link Mapy: {item['maps_link']}\n")
                f.write("-" * 40 + "\n\n")
        print(f"\n{Fore.GREEN}[$] ZAPISANO PRAWIDŁOWO:{Style.RESET_ALL}\n{full_path}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Błąd zapisu: {e}{Style.RESET_ALL}")

def main():
    clear_screen()
    print_banner()
    
    # Proste zbieranie danych
    print(f"{Fore.YELLOW}[?] Słowo kluczowe: {Style.RESET_ALL}", end="")
    keyword = input()
    print(f"{Fore.YELLOW}[?] Ile leadów: {Style.RESET_ALL}", end="")
    try:
        limit = int(input())
    except:
        limit = 1
        
    leads = scrape_google_maps(keyword, "Polska", limit)
    
    if leads:
        save_to_phone(leads)

if __name__ == "__main__":
    main()
    
