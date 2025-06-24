import requests
import time
import schedule
import logging
import re
from typing import List, Dict, Optional
from colorama import init, Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Initialize rich console for enhanced UI
console = Console()

# ASCII art and author credit
ASCII_ART = f"""
{Fore.CYAN + Style.BRIGHT}
 @@@@@@@@   @@@@@@   @@@@@@@   @@@       @@@  @@@  @@@
@@@@@@@@@  @@@@@@@@  @@@@@@@@  @@@       @@@  @@@@ @@@
!@@        @@!  @@@  @@!  @@@  @@!       @@!  @@!@!@@@
!@!        !@!  @!@  !@   @!@  !@!       !@!  !@!!@!@!
!@! @!@!@  @!@  !@!  @!@!@!@   @!!       !!@  @!@ !!@!
!!! !!@!!  !@!  !!!  !!!@!!!!  !!!       !!!  !@!  !!!
:!!   !!:  !!:  !!!  !!:  !!!  !!:       !!:  !!:  !!!
:!:   !::  :!:  !:!  :!:  !:!   :!:      :!:  :!:  !:!
 ::: ::::  ::::: ::   :: ::::   :: ::::   ::   ::   ::
 :: :: :    : :  :   :: : ::   : :: : :  :    ::    :

@@@@@@@@@@   @@@@@@@@  @@@@@@@@@@   @@@@@@@@
@@@@@@@@@@@  @@@@@@@@  @@@@@@@@@@@  @@@@@@@@
@@! @@! @@!  @@!       @@! @@! @@!  @@!
!@! !@! !@!  !@!       !@! !@! !@!  !@!
@!! !!@ @!@  @!!!:!    @!! !!@ @!@  @!!!:!
!@!   ! !@!  !!!!!:    !@!   ! !@!  !!!!!:
!!:     !!:  !!:       !!:     !!:  !!:
:!:     :!:  :!:       :!:     :!:  :!:
:::     ::    :: ::::  :::     ::    :: ::::
 :      :    : :: ::    :      :    : :: ::
{Style.RESET_ALL}
{Fore.MAGENTA + Style.BRIGHT}Author by: t.me/airdropdxns 🚀{Style.RESET_ALL}
"""

# API endpoints
BASE_URL = "https://www.goblin.meme/api"
SESSION_URL = f"{BASE_URL}/auth/session"
BOX_URL = f"{BASE_URL}/box"
BOX_ID = "6856701d223b22873ed1d730"  # From provided data
START_MINING_URL = f"{BOX_URL}/{BOX_ID}/start"

# Headers template
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}

class ProxyManager:
    def __init__(self, proxy_file: str = "proxy.txt"):
        self.proxy_file = proxy_file
        self.proxies = self._load_proxies()
        self.current_index = 0

    def _load_proxies(self) -> List[str]:
        """Load proxies from proxy.txt"""
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f if line.strip()]
            valid_proxies = []
            for proxy in proxies:
                if self._validate_proxy_format(proxy):
                    if not proxy.startswith('http://') and not proxy.startswith('https://'):
                        proxy = 'http://' + proxy
                    valid_proxies.append(proxy)
                    console.print(f"[bold green]✅ Proxy valid: {proxy} 🛡️[/bold green]")
                else:
                    console.print(f"[bold yellow]⚠ Invalid proxy format, ignored: {proxy} 🚫[/bold yellow]")
            console.print(Panel(f"Total proxies loaded: {len(valid_proxies)} 🎉", style="cyan"))
            return valid_proxies
        except FileNotFoundError:
            console.print("[bold blue]ℹ proxy.txt not found, running without proxies 📡[/bold blue]")
            return []
        except Exception as e:
            console.print(f"[bold red]❌ Error loading proxies: {str(e)} 😢[/bold red]")
            return []

    def _validate_proxy_format(self, proxy: str) -> bool:
        """Validate proxy format"""
        pattern = r'^(?:http[s]?://)?(?:\S+:\S+@)?\S+:\d+$'
        return bool(re.match(pattern, proxy))

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        proxy_str = self.proxies[self.current_index % len(self.proxies)]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return {"http": proxy_str, "https": proxy_str}

def read_tokens() -> List[str]:
    """Read auth tokens from token.txt"""
    try:
        with open('token.txt', 'r') as file:
            tokens = [line.strip() for line in file if line.strip()]
        console.print(Panel(f"Loaded {len(tokens)} tokens from token.txt 🔑", style="green"))
        return tokens
    except FileNotFoundError:
        console.print("[bold red]❌ token.txt file not found 😕[/bold red]")
        return []

def check_session(token: str, proxies: Optional[Dict[str, str]] = None) -> bool:
    """Check if session is valid"""
    headers = HEADERS.copy()
    headers["cookie"] = f"__Secure-next-auth.session-token={token}"
    
    try:
        console.print(f"[bold yellow]⏳ Checking session for token: {token[:20]}... 🔍[/bold yellow]")
        response = requests.get(SESSION_URL, headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("user"):
                console.print(Panel(f"Valid session for user: {data['user']['name']} ✅", style="green"))
                return True
        console.print(f"[bold yellow]⚠ Invalid session for token: {token[:20]}... 🚫[/bold yellow]")
        return False
    except Exception as e:
        console.print(f"[bold red]❌ Session check error: {str(e)} 😢[/bold red]")
        return False

def check_and_mine(token: str, proxies: Optional[Dict[str, str]] = None) -> bool:
    """Check box status and start mining if possible"""
    headers = HEADERS.copy()
    headers["cookie"] = f"__Secure-next-auth.session-token={token}"
    
    try:
        console.print(f"[bold yellow]⏳ Checking box status for token: {token[:20]}... 📦[/bold yellow]")
        response = requests.get(f"{BOX_URL}/{BOX_ID}", headers=headers, proxies=proxies, timeout=10)
        if response.status_code != 200:
            console.print(f"[bold red]❌ Failed to check box status: {response.status_code} 😢[/bold red]")
            return False
            
        box_data = response.json()
        
        if box_data.get("hasBox") and not box_data.get("isReady"):
            console.print(Panel(f"Box already mining, ready at: {box_data.get('readyAt')} ⏰", style="blue"))
            return True
            
        if not box_data.get("hasBox"):
            console.print(f"[bold yellow]⏳ Starting mining for token: {token[:20]}... ⛏️[/bold yellow]")
            response = requests.post(START_MINING_URL, headers=headers, proxies=proxies, timeout=10)
            if response.status_code == 200:
                mining_data = response.json()
                console.print(Panel(f"Mining started: {mining_data.get('message')} 🎉", style="green"))
                return True
            else:
                console.print(f"[bold red]❌ Failed to start mining: {response.status_code} 😢[/bold red]")
                return False
                
    except Exception as e:
        console.print(f"[bold red]❌ Mining error: {str(e)} 😢[/bold red]")
        return False

def process_accounts(use_proxy: bool):
    """Process all accounts with proxy rotation if enabled"""
    tokens = read_tokens()
    if not tokens:
        console.print("[bold red]❌ No tokens found in token.txt 😕[/bold red]")
        return
        
    proxy_manager = ProxyManager() if use_proxy else None
    
    for i, token in enumerate(tokens):
        proxy = proxy_manager.get_next_proxy() if use_proxy and proxy_manager else None
        if proxy:
            console.print(f"[bold cyan]🛡️ Using proxy {proxy['http']} for token: {token[:20]}... 🌐[/bold cyan]")
        else:
            console.print(f"[bold blue]📡 No proxy used for token: {token[:20]}... 🌍[/bold blue]")
        
        if check_session(token, proxy):
            check_and_mine(token, proxy)

def main():
    """Main function to schedule mining"""
    # Print ASCII art and author credit
    print(ASCII_ART)
    
    # Display welcome panel
    console.print(Panel(
        Text("🚀 Goblin Meme Auto-Mining Bot 🚀", style="bold cyan", justify="center"),
        style="cyan",
        border_style="bold cyan",
        padding=(1, 2)
    ))
    
    # Prompt for proxy usage
    while True:
        console.print("[bold magenta]🛡️ Use proxy? (y/n): [/bold magenta]", end="")
        use_proxy_input = input().strip().lower()
        if use_proxy_input in ['y', 'n']:
            use_proxy = use_proxy_input == 'y'
            console.print(f"[bold green]✅ Proxy usage set to: {'Enabled' if use_proxy else 'Disabled'} 🎉[/bold green]")
            break
        console.print("[bold red]❌ Invalid input. Please enter 'y' or 'n'. 😕[/bold red]")
    
    # Run immediately on start
    console.print(Panel("Starting initial mining run... ⛏️", style="yellow"))
    process_accounts(use_proxy)
    
    # Schedule to run every 24 hours
    schedule.every(24).hours.do(process_accounts, use_proxy=use_proxy)
    console.print(Panel("Scheduled mining every 24 hours 📅", style="green"))
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()