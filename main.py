#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonerSkiddMax LeadGen v2.0
Scraper Google Maps bez API — parsuje APP_INITIALIZATION_STATE z HTML.
Autor bazowy: @monerthetimeprojector | Rebuild: ENI
"""

import os
import re
import sys
import json
import time
import csv
import random
import urllib.parse
from pathlib import Path

try:
    import requests
except ImportError:
    print("[!] Brak modułu 'requests'. Zainstaluj: pip install requests")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class _Dummy:
        def __getattr__(self, _): return ""
    Fore = Style = _Dummy()

# ─────────────────────────── KONFIG ───────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.7,en;q=0.6",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[\s\-]?)?(?:$?\d{2,4}$?[\s\-]?)?\d{3}[\s\-]?\d{2,3}[\s\-]?\d{2,3}"
)
URL_REGEX = re.compile(r"https?://(?!(?:www\.)?google\.)[^\s\"']+")

# ─────────────────────────── UI ───────────────────────────
def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")

def print_banner():
    banner = f"""{Fore.MAGENTA}
  __  __                       ____  _    _     _     _
 |  \\/  | ___  _ __   ___ _ __/ ___|| | _(_) __| | __| |_ __ ___   __ ___  __
 | |\\/| |/ _ \\| '_ \\ / _ \\ '__\\___ \\| |/ / |/ _` |/ _` | '_ ` _ \\ / _` \\ \\/ /
 | |  | | (_) | | | |  __/ |   ___) |   <| | (_| | (_| | | | | | | (_| |>  <
 |_|  |_|\\___/|_| |_|\\___|_|  |____/|_|\\_\\_|\\__,_|\\__,_|_| |_| |_|\\__,_/_/\\_/
{Style.RESET_ALL}
    {Fore.CYAN}[+] Credits: @monerthetimeprojector
    [+] LeadGen v2.0 — Real Google Maps Scraper (no API)
{Style.RESET_ALL}"""
    print(banner)

def ask(prompt, default=None):
    hint = f" {Fore.WHITE}[{default}]{Style.RESET_ALL}" if default else ""
    val = input(f"{Fore.YELLOW}[?] {prompt}{hint}: {Style.RESET_ALL}").strip()
    return val if val else (default or "")

def info(msg):    print(f"{Fore.CYAN}[i]{Style.RESET_ALL} {msg}")
def ok(msg):      print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")
def warn(msg):    print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")
def err(msg):     print(f"{Fore.RED}[x]{Style.RESET_ALL} {msg}")

# ─────────────────────────── SCRAPER ───────────────────────────
def build_maps_url(query: str, hl="pl", gl="pl") -> str:
    q = urllib.parse.quote_plus(query)
    return f"https://www.google.com/maps/search/{q}?hl={hl}&gl={gl}"

def get_maps_link(name: str, address: str) -> str:
    query = f"{name} {address}".strip()
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(query)}"

def _session():
    s = requests.Session()
    headers = DEFAULT_HEADERS.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    s.headers.update(headers)
    return s

def fetch_maps_html(query: str, retries=3, timeout=25) -> str | None:
    url = build_maps_url(query)
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            s = _session()
            # rozgrzewka ciasteczek
            s.get("https://www.google.com/", timeout=timeout)
            time.sleep(random.uniform(0.4, 1.1))
            r = s.get(url, timeout=timeout)
            if r.status_code == 200 and "APP_INITIALIZATION_STATE" in r.text:
                return r.text
            warn(f"Próba {attempt}: HTTP {r.status_code}, brak payloadu — retry...")
        except requests.RequestException as e:
            last_exc = e
            warn(f"Próba {attempt}: {e}")
        time.sleep(random.uniform(1.2, 2.5) * attempt)
    if last_exc:
        err(f"Ostateczny błąd sieci: {last_exc}")
    return None

def extract_app_state(html: str):
    """Wyciąga JSON z window.APP_INITIALIZATION_STATE."""
    m = re.search(
        r"APP_INITIALIZATION_STATE\s*=\s*(

$$
.+?
$$

)\s*;\s*(?:window\.APP_FLAGS|window\.)",
        html, re.DOTALL,
    )
    if not m:
        # bardziej luźny fallback
        m = re.search(r"APP_INITIALIZATION_STATE\s*=\s*(

$$
.+?
$$

);", html, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None

def _safe(obj, *path, default=None):
    cur = obj
    for p in path:
        try:
            cur = cur[p]
        except (IndexError, KeyError, TypeError):
            return default
    return cur if cur is not None else default

def _find_phone(blob_str: str) -> str | None:
    # szuka polskich/pl-podobnych numerów w surowym stringu
    candidates = PHONE_REGEX.findall(blob_str)
    for c in candidates:
        digits = re.sub(r"\D", "", c)
        if 9 <= len(digits) <= 13:
            return c.strip()
    return None

def _find_website(blob_str: str) -> str | None:
    m = URL_REGEX.search(blob_str)
    return m.group(0).rstrip("\",') ") if m else None

def parse_places(app_state) -> list[dict]:
    """
    Struktura Maps: app_state[3][2] to string ")]}'\n" + JSON.
    W środku pod [0][1] leży lista wyników; każdy entry ma płatny szczegół pod [14].
    """
    results = []
    raw = _safe(app_state, 3, 2)
    if not isinstance(raw, str):
        return results
    if raw.startswith(")]}'"):
        raw = raw[4:]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return results

    entries = _safe(parsed, 0, 1, default=[]) or []
    for entry in entries:
        place = _safe(entry, 14)
        if not place:
            continue
        try:
            name = _safe(place, 11) or "—"
            address = _safe(place, 39) or _safe(place, 18) or "—"
            lat = _safe(place, 9, 2)
            lng = _safe(place, 9, 3)
            rating = _safe(place, 4, 7)
            reviews = _safe(place, 4, 8)
            category = _safe(place, 13, 0)
            # telefon i www — szukamy w surowym reprezentacji place
            blob = json.dumps(place, ensure_ascii=False)
            phone = _find_phone(blob) or "—"
            website = _find_website(blob) or "—"

            if lat and lng:
                maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
            else:
                maps_link = get_maps_link(name, address if address != "—" else "")

            results.append({
                "name": name,
                "category": category or "—",
                "address": address,
                "phone": phone,
                "website": website,
                "rating": rating if rating is not None else "—",
                "reviews": reviews if reviews is not None else "—",
                "lat": lat,
                "lng": lng,
                "maps_link": maps_link,
            })
        except Exception:
            continue
    return results

def scrape_google_maps(keyword: str, region: str, limit: int) -> list[dict]:
    query = f"{keyword} {region}".strip()
    info(f"Wysyłam żądanie: {Fore.WHITE}{query}{Style.RESET_ALL}")
    html = fetch_maps_html(query)
    if not html:
        return []
    state = extract_app_state(html)
    if not state:
        err("Nie udało się wyciągnąć APP_INITIALIZATION_STATE (Google mógł zmienić strukturę lub cię capchował).")
        return []
    places = parse_places(state)
    if not places:
        warn("Parser nie znalazł miejsc — spróbuj mocniejszego słowa kluczowego lub zmień region.")
    return places[:limit] if limit > 0 else places

# ─────────────────────────── ZAPIS ───────────────────────────
def resolve_output_dir() -> Path:
    candidates = [
        Path("/sdcard/Download"),
        Path("/storage/emulated/0/Download"),
        Path.home() / "storage" / "downloads",
        Path.home() / "Downloads",
        Path.cwd(),
    ]
    for c in candidates:
        try:
            if c.exists() and os.access(c, os.W_OK):
                return c
        except Exception:
            continue
    return Path.cwd()

def save_txt(data, path: Path):
    with path.open("w", encoding="utf-8") as f:
        f.write("=== MONERSKIDDMAX LEADS ===\n\n")
        for i, it in enumerate(data, 1):
            f.write(f"[{i}] {it['name']}\n")
            f.write(f"  Kategoria: {it['category']}\n")
            f.write(f"  Adres:     {it['address']}\n")
            f.write(f"  Telefon:   {it['phone']}\n")
            f.write(f"  WWW:       {it['website']}\n")
            f.write(f"  Ocena:     {it['rating']} ({it['reviews']} opinii)\n")
            if it["lat"] and it["lng"]:
                f.write(f"  Koordy:    {it['lat']}, {it['lng']}\n")
            f.write(f"  Mapy:      {it['maps_link']}\n")
            f.write("-" * 60 + "\n")

def save_csv(data, path: Path):
    fields = ["name","category","address","phone","website","rating","reviews","lat","lng","maps_link"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for it in data:
            w.writerow({k: it.get(k, "") for k in fields})

def save_json(data, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_leads(data):
    out_dir = resolve_output_dir()
    info(f"Katalog zapisu: {Fore.WHITE}{out_dir}{Style.RESET_ALL}")
    name = ask("Nazwa pliku (bez rozszerzenia)", default="leady_output")
    fmt = ask("Format: [1] TXT  [2] CSV  [3] JSON  [4] wszystkie", default="1")

    saved = []
    try:
        if fmt in ("1", "4"):
            p = out_dir / f"{name}.txt"; save_txt(data, p); saved.append(p)
        if fmt in ("2", "4"):
            p = out_dir / f"{name}.csv"; save_csv(data, p); saved.append(p)
        if fmt in ("3", "4"):
            p = out_dir / f"{name}.json"; save_json(data, p); saved.append(p)
        if not saved:
            p = out_dir / f"{name}.txt"; save_txt(data, p); saved.append(p)
    except Exception as e:
        err(f"Błąd zapisu: {e}")
        return

    ok("Zapisano:")
    for p in saved:
        print(f"    {Fore.GREEN}→ {p}{Style.RESET_ALL}")

def print_preview(data):
    print()
    for i, it in enumerate(data, 1):
        print(f"{Fore.MAGENTA}[{i}] {it['name']}{Style.RESET_ALL}  {Fore.WHITE}({it['category']}){Style.RESET_ALL}")
        print(f"    {Fore.CYAN}Adres:{Style.RESET_ALL}   {it['address']}")
        print(f"    {Fore.CYAN}Tel:{Style.RESET_ALL}     {it['phone']}")
        print(f"    {Fore.CYAN}WWW:{Style.RESET_ALL}     {it['website']}")
        print(f"    {Fore.CYAN}Ocena:{Style.RESET_ALL}   {it['rating']} ({it['reviews']} opinii)")
        print(f"    {Fore.CYAN}Mapy:{Style.RESET_ALL}    {Fore.BLUE}{it['maps_link']}{Style.RESET_ALL}")
        print()

# ─────────────────────────── MENU ───────────────────────────
def menu():
    print(f"""
{Fore.MAGENTA}╔══════════════════════════════════════╗
║           MENU  GŁÓWNE               ║
╠══════════════════════════════════════╣
║  1) Scrapuj Google Maps              ║
║  2) Generuj tylko link do Map        ║
║  3) O programie                      ║
║  0) Wyjście                          ║
╚══════════════════════════════════════╝{Style.RESET_ALL}""")
    return ask("Wybór", default="1")

def action_scrape():
    keyword = ask("Słowo kluczowe (np. fizjoterapeuta)")
    if not keyword:
        err("Musisz podać słowo kluczowe.")
        return
    region = ask("Region / miasto", default="Polska")
    try:
        limit = int(ask("Ile leadów maksymalnie", default="20"))
    except ValueError:
        limit = 20

    t0 = time.time()
    leads = scrape_google_maps(keyword, region, limit)
    dt = time.time() - t0
        if not leads:
        err("Zero wyników. Spróbuj innego słowa/regionu lub odczekaj chwilę (Google mógł ograniczyć).")
        return

    ok(f"Znaleziono {len(leads)} leadów w {dt:.2f}s")
    print_preview(leads)

    if ask("Zapisać do pliku? (t/n)", default="t").lower().startswith("t"):
        save_leads(leads)

def action_link():
    name = ask("Nazwa miejsca")
    address = ask("Adres / miasto", default="")
    if not name and not address:
        err("Podaj przynajmniej jedno pole.")
        return
    link = get_maps_link(name, address)
    ok("Wygenerowany link:")
    print(f"    {Fore.BLUE}{link}{Style.RESET_ALL}")

def action_about():
    print(f"""
{Fore.CYAN}MonerSkiddMax LeadGen v2.0{Style.RESET_ALL}
  • Scrapuje Google Maps bez API (parsing APP_INITIALIZATION_STATE).
  • Wyciąga: nazwa, kategoria, adres, telefon, www, ocena, opinie, koordynaty.
  • Eksport: TXT / CSV / JSON.
  • Automatyczny wybór katalogu (Termux/Android/Linux/Win).
  • Rotacja User-Agent, retry, cookie warmup.

{Fore.YELLOW}Uwaga:{Style.RESET_ALL} Google może zmienić strukturę HTML lub nałożyć CAPTCHA.
Jeśli parser nic nie zwraca — poczekaj lub zmień sieć/VPN.
""")

def main():
    try:
        clear_screen()
        print_banner()
        while True:
            choice = menu()
            if choice == "1":
                action_scrape()
            elif choice == "2":
                action_link()
            elif choice == "3":
                action_about()
            elif choice == "0":
                ok("Do zobaczenia, mordo. 👋")
                break
            else:
                warn("Nieznana opcja.")
            input(f"\n{Fore.WHITE}[Enter] aby wrócić do menu...{Style.RESET_ALL}")
            clear_screen()
            print_banner()
    except KeyboardInterrupt:
        print()
        warn("Przerwano przez użytkownika (Ctrl+C).")
        sys.exit(0)

if __name__ == "__main__":
    main()
