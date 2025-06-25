import requests
import time
import schedule
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from colorama import init, Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import pytz
import threading

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
BOX_ID = "6856701d223b22873ed1d730"  # Goblin Box ID
BOX_NAME = "Goblin Box"
START_MINING_URL = f"{BOX_URL}/{BOX_ID}/start"
OPEN_BOX_URL = f"{BOX_URL}/{BOX_ID}/claim"
MISSION_URL = f"{BOX_URL}/{BOX_ID}/mission"

# Headers template
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "content-type": "application/json"
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
    headers["cookie"] = f"__Secure-next-auth.session-token={token}; referral=T43O9C"
    
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

def check_box_status(token: str, proxies: Optional[Dict[str, str]] = None) -> Optional[Dict]:
    """Check box status for Goblin Box"""
    headers = HEADERS.copy()
    headers["cookie"] = f"__Secure-next-auth.session-token={token}; referral=T43O9C"
    
    try:
        console.print(f"[bold yellow]⏳ Checking status for {BOX_NAME} with token: {token[:20]}... 📦[/bold yellow]")
        response = requests.get(f"{BOX_URL}/{BOX_ID}", headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            return response.json()
        console.print(f"[bold red]❌ Failed to check box status for {BOX_NAME}: {response.status_code} 😢[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]❌ Box status check error for {BOX_NAME}: {str(e)} 😢[/bold red]")
        return None

def start_mining(token: str, proxies: Optional[Dict[str, str]] = None) -> bool:
    """Start mining for Goblin Box if not already active"""
    headers = HEADERS.copy()
    headers["cookie"] = f"__Secure-next-auth.session-token={token}; referral=T43O9C"
    
    try:
        console.print(f"[bold yellow]⏳ Starting mining for {BOX_NAME} with token: {token[:20]}... ⛏️[/bold yellow]")
        response = requests.post(START_MINING_URL, headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            mining_data = response.json()
            console.print(Panel(f"Mining started for {BOX_NAME}: {mining_data.get('message')} 🎉", style="green"))
            return True
        console.print(f"[bold red]❌ Failed to start mining for {BOX_NAME}: {response.status_code} 😢[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]❌ Mining error for {BOX_NAME}: {str(e)} 😢[/bold red]")
        return False

def engage_mission(token: str, proxies: Optional[Dict[str, str]] = None) -> bool:
    """Mark mission as completed for Goblin Box"""
    headers = HEADERS.copy()
    headers["cookie"] = f"__Secure-next-auth.session-token={token}; referral=T43O9C"
    
    try:
        console.print(f"[bold yellow]⏳ Engaging mission for {BOX_NAME} with token: {token[:20]}... 📱[/bold yellow]")
        response = requests.post(MISSION_URL, headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            mission_data = response.json()
            if mission_data.get("message") == "Mission marked as completed.":
                console.print(Panel(f"Mission marked as completed for {BOX_NAME} 🎉", style="green"))
                return True
            console.print(f"[bold yellow]⚠ Mission engagement response for {BOX_NAME}: {mission_data.get('message')} 🚫[/bold yellow]")
            return False
        console.print(f"[bold red]❌ Failed to engage mission for {BOX_NAME}: {response.status_code} 😢[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]❌ Mission engagement error for {BOX_NAME}: {str(e)} 😢[/bold red]")
        return False

def claim_box(token: str, proxies: Optional[Dict[str, str]] = None) -> bool:
    """Claim box contents for Goblin Box"""
    headers = HEADERS.copy()
    headers["cookie"] = f"__Secure-next-auth.session-token={token}; referral=T43O9C"
    
    try:
        console.print(f"[bold yellow]⏳ Claiming {BOX_NAME} with token: {token[:20]}... 🎁[/bold yellow]")
        response = requests.post(OPEN_BOX_URL, headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            claim_data = response.json()
            if claim_data.get("message") == "Box opened! Prize credited.":
                console.print(Panel(f"Box opened for {BOX_NAME}! Prize: {claim_data.get('prizeAmount')} ({claim_data.get('prizeType')}), New Balance: {claim_data.get('newBalance')} 🎉", style="green"))
                return True
            console.print(f"[bold yellow]⚠ Claim response for {BOX_NAME}: {claim_data.get('message')} 🚫[/bold yellow]")
            return False
        console.print(f"[bold red]❌ Failed to claim {BOX_NAME}: {response.status_code} 😢[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]❌ Claim error for {BOX_NAME}: {str(e)} 😢[/bold red]")
        return False

def schedule_claim(token: str, wait_time: float, proxies: Optional[Dict[str, str]] = None):
    """Schedule the mission engagement and box claiming after wait_time seconds"""
    def claim_task():
        box_data = check_box_status(token, proxies)
        if not box_data:
            return

        if box_data.get("hasBox") and box_data.get("isReady") and not box_data.get("opened"):
            if not box_data.get("missionCompleted"):
                if engage_mission(token, proxies):
                    box_data["missionCompleted"] = True
                else:
                    console.print(f"[bold red]❌ Mission not completed for {BOX_NAME} with token: {token[:20]}..., cannot claim 😢[/bold red]")
                    return
            if claim_box(token, proxies):
                box_data = check_box_status(token, proxies)
                if not box_data:
                    return
                if not box_data.get("hasBox"):
                    start_mining(token, proxies)

    console.print(f"[bold yellow]⏳ Scheduling claim for {BOX_NAME} with token: {token[:20]}... in {wait_time/3600:.2f} hours ⏰[/bold yellow]")
    schedule.every(wait_time).seconds.do(claim_task).tag(f"claim_{token[:20]}")

def process_account(token: str, proxies: Optional[Dict[str, str]] = None):
    """Process the Goblin Box for a single account"""
    if not check_session(token, proxies):
        return

    box_data = check_box_status(token, proxies)
    if not box_data:
        return

    current_time = datetime.now(pytz.UTC)

    if box_data.get("hasBox") and not box_data.get("isReady"):
        try:
            ready_at = datetime.strptime(box_data.get("readyAt"), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
            wait_time = (ready_at - current_time).total_seconds()
            if wait_time > 0:
                console.print(Panel(f"{BOX_NAME} already mining, ready at: {box_data.get('readyAt')} ⏰", style="blue"))
                # Schedule claim instead of blocking
                schedule_claim(token, wait_time, proxies)
            else:
                # If ready time is in the past, proceed to mission and claim
                if not box_data.get("missionCompleted"):
                    if engage_mission(token, proxies):
                        box_data["missionCompleted"] = True
                    else:
                        console.print(f"[bold red]❌ Mission not completed for {BOX_NAME}, cannot claim 😢[/bold red]")
                        return
                if claim_box(token, proxies):
                    box_data = check_box_status(token, proxies)
                    if not box_data:
                        return
                    if not box_data.get("hasBox"):
                        start_mining(token, proxies)
        except ValueError as e:
            console.print(f"[bold red]❌ Error parsing readyAt time for {BOX_NAME}: {str(e)} 😢[/bold red]")
            return

    elif box_data.get("hasBox") and box_data.get("isReady") and not box_data.get("opened"):
        if not box_data.get("missionCompleted"):
            if engage_mission(token, proxies):
                box_data["missionCompleted"] = True
            else:
                console.print(f"[bold red]❌ Mission not completed for {BOX_NAME}, cannot claim 😢[/bold red]")
                return
        if claim_box(token, proxies):
            box_data = check_box_status(token, proxies)
            if not box_data:
                return
            if not box_data.get("hasBox"):
                start_mining(token, proxies)

    elif not box_data.get("hasBox"):
        start_mining(token, proxies)

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
        
        process_account(token, proxy)

def main():
    """Main function to schedule mining and box claiming"""
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
    console.print(Panel(f"Starting initial mining run for {BOX_NAME}... ⛏️", style="yellow"))
    process_accounts(use_proxy)
    
    # Schedule to run every 4 hours to check status and claim
    schedule.every(4).hours.do(process_accounts, use_proxy=use_proxy)
    console.print(Panel(f"Scheduled mining and claiming for {BOX_NAME} every 4 hours 📅", style="green"))
    
    # Run scheduled tasks in a separate thread to avoid blocking
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        console.print("[bold yellow]⚠ Script terminated by user. Exiting... 👋[/bold yellow]")
        exit(0)

if __name__ == "__main__":
    main()
