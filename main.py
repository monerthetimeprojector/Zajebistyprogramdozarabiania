import os
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
    {Fore.CYAN}[+] Credits: @monerthetimeprojector
    [+] LinkGen v1.1 - Wersja stabilna z linkami do map
    {Style.RESET_ALL}"""
    print(banner)

def get_maps_link(name, address):
    # Funkcja tworzy bezpieczny link do Map Google
    query = f"{name} {address}".replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={query}"

def save_to_phone(keyword, limit):
    print(f"\n{Fore.YELLOW}[?] Podaj nazwę pliku (np. leady_{keyword}):{Style.RESET_ALL}")
    filename = input(f"{Fore.CYAN}root@monerskiddmax:~# {Style.RESET_ALL}")
    if not filename: filename = "leady_output"
    
    full_path = f"/sdcard/Download/{filename}.txt"
    
    # Przykładowa generacja danych (zamiast błędnego scrapa)
    # Tutaj możesz wkleić listę, którą chcesz przetworzyć
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"=== LEADY: {keyword.upper()} ===\n\n")
            for i in range(1, limit + 1):
                name = f"{keyword.capitalize()} nr {i}"
                address = "Polska"
                link = get_maps_link(name, address)
                
                f.write(f"Nazwa: {name}\n")
                f.write(f"Lokalizacja: {address}\n")
                f.write(f"LINK DO MAP: {link}\n")
                f.write("-" * 40 + "\n")
        print(f"\n{Fore.GREEN}[$] ZAPISANO PRAWIDŁOWO:{Style.RESET_ALL}\n{full_path}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Błąd zapisu: {e}{Style.RESET_ALL}")

def main():
    clear_screen()
    print_banner()
    
    keyword = input(f"{Fore.YELLOW}[?] Słowo kluczowe: {Style.RESET_ALL}")
    try:
        limit = int(input(f"{Fore.YELLOW}[?] Ile leadów: {Style.RESET_ALL}"))
    except:
        limit = 5
        
    save_to_phone(keyword, limit)

if __name__ == "__main__":
    main()
    
