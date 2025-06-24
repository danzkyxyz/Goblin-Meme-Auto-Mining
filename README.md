# 🚀 Goblin Meme Auto-Mining Bot ⛏️
Welcome to the Goblin Meme Auto-Mining Bot! This Python script automates the mining process for the Goblin Meme platform, supporting multiple accounts and optional proxy usage. It runs every 24 hours, checks session validity, and starts mining with vibrant console output powered by colorama and rich. 🌟

Author: t.me/airdropdxns 📩

## 🎯 Features
- Multi-Account Support 🔑: Handles multiple accounts using auth tokens from token.txt.
- Optional Proxy Rotation 🛡️: Uses proxies from proxy.txt for each account (optional).
- Automated Mining ⛏️: Checks box status and starts mining every 24 hours.
- Colorful Console Output 🌈: Enhanced with colorama and rich for eye-catching logs.
- Error Handling 🛠️: Robust handling of network issues and invalid tokens/proxies.
- Scheduled Execution 📅: Runs automatically every 24 hours using schedule.

## 📋 Prerequisites
- Python 3.10 🐍
- A token.txt file with Goblin Meme auth tokens (one per line).
- Optionally, a proxy.txt file with proxies in the format http://user:pass@host:port or http://host:port.

## 🛠️ Installation
### Clone Repository 📂
```bash
git clone https://github.com/danzkyxyz/Goblin-Meme-Auto-Mining.git
cd Goblin-Meme-Auto-Mining
```
### Install Dependencies 📦
```bash
pip install -r requirements.txt
```
### Prepare Configuration Files 📝
Create a token.txt file in the project directory with your Goblin Meme auth tokens, one per line:
```bash
eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0...
eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0...
```
Optionally, create a proxy.txt file with proxies (one per line):
```bash
http://user:pass@host:port
http://host:port
```

# 🚀 Usage
## Run the Script 🏃‍♂️
```bash
python main.py
```
or
```bash
python3 main.py
```

## Follow the Prompt ❓
When prompted with Use proxy? (y/n):, enter:
- y to enable proxy rotation (requires proxy.txt).
- n to run without proxies.

## What Happens Next? 🌟
- The script displays a colorful ASCII art banner and author credit. 🎨
- It loads tokens from token.txt and proxies from proxy.txt (if enabled).
- For each account, it validates the session and starts mining if possible.
- Logs are displayed in the terminal with vibrant colors and emojis. 📜
- The bot runs immediately and then every 24 hours. ⏰

# 📁 File Structure
```bash
goblin-meme-auto-mining-bot/
├── main.py             # Main script 🚀
├── token.txt           # Auth tokens (create manually) 🔑
├── proxy.txt           # Proxies (optional, create manually) 🛡️
├── requirements.txt    # Python dependencies 📦
└── README.md           # This file 📖
```

# ⚠️ Security Notes
Keep Files Secure 🔒: The token.txt and proxy.txt files contain sensitive information (auth tokens and proxy credentials). Ensure they are stored securely and not shared publicly.

# Join our Channel
Https://t.me/airdropdxns
