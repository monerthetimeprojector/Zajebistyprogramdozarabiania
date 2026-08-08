import requests
from bs4 import BeautifulSoup
import urllib.parse
from colorama import init, Fore, Style

init(autoreset=True)

# KONFIGURACJA PROXY (Wpisz swoje proxy w formacie: http://user:pass@ip:port)
# Jeśli nie używasz proxy, zostaw None
PROXY = {
    'http': None,
    'https': None
}

def get_leads(keyword, limit):
    print(f"\n{Fore.CYAN}[*] Przeszukuję Google dla: {keyword}...{Style.RESET_ALL}")
    
    # Budowanie URL (używamy duckduckgo lub google - google bez API jest trudne)
    query = urllib.parse.quote(keyword)
    url = f"https://www.google.com/search?q={query}&tbm=lcl" # tbm=lcl to filtr map
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        # Prawdziwe zapytanie z proxy
        response = requests.get(url, headers=headers, proxies=PROXY, timeout=10)
        
        if response.status_code != 200:
            print(f"{Fore.RED}[!] Błąd połączenia: {response.status_code}. Zmień proxy!")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pamiętaj: Google Maps dynamicznie zmienia klasy. To jest bardzo podstawowy parser.
        results = []
        # Przykładowe szukanie kontenerów (klasy mogą się zmieniać!)
        containers = soup.find_all('div', class_='tZPcob') 
        
        for container in containers[:limit]:
            name = container.get_text() # Uproszczone
            results.append({"name": name, "address": "Wymaga zaawansowanego parsera"})
            
        return results
    except Exception as e:
        print(f"{Fore.RED}[!] Błąd scrapowania: {e}{Style.RESET_ALL}")
        return []

def main():
    keyword = input(f"{Fore.YELLOW}Słowo kluczowe: {Style.RESET_ALL}")
    limit = int(input(f"{Fore.YELLOW}Ile leadów: {Style.RESET_ALL}"))
    
    leads = get_leads(keyword, limit)
    
    if leads:
        print(f"{Fore.GREEN}[+] Znaleziono {len(leads)} leadów.{Style.RESET_ALL}")
        # Zapis do pliku... (tak jak w poprzednim kodzie)
    else:
        print(f"{Fore.RED}[!] Nic nie znaleziono. Sprawdź proxy lub czy Google Cię nie blokuje.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
    
