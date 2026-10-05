cd ~/flask-c2-framework

cat > README.md << 'EOF'
# Flask C2 Framework

> A minimal, educational Command & Control (C2) framework built with Flask, SQLite, and AES-256-GCM encryption. Designed to demonstrate red team infrastructure concepts for portfolio and lab use.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ⚠️ Disclaimer

This project is intended **strictly for authorized security testing, education, and research**. Never deploy against systems you do not own or have explicit written permission to test. The author assumes no liability for misuse.

---

## ✨ Features

- **AES-256-GCM encrypted communications** — All post-registration traffic between implant and server is encrypted.
- **Jittered beaconing** — Randomized sleep intervals to evade pattern-based network detection.
- **Web-based operator dashboard** — Dark-themed UI to manage agents, queue tasks, and view live output.
- **Asynchronous task queue** — Commands are queued server-side; agents pull and execute them on next check-in.
- **Persistent agent tracking** — SQLite storage of agents, tasks, and results across server restarts.
- **Auto-refreshing output** — Dashboard polls for new task results every 4 seconds.

---

## 🏗️ Architecture
┌─────────────┐ 1. register (plaintext, one-time) ┌──────────────┐
│ Implant │ ───────────────────────────────────► │ │
│ (agent.py) │ ◄─────── returns AES-256 key ─────── │ │
│ │ │ │
│ │ 2. beacon (agent→server) │ Flask C2 │
│ │ ───────────────────────────────────► │ Server │
│ │ ◄─── encrypted task list ────────── │ │
│ │ │ │
│ │ 3. result (agent→server) │ │
│ │ ──── encrypted command output ─────► │ │
└─────────────┘ └──────┬───────┘
│
▼
┌─────────────────┐
│ Operator Web │
│ Dashboard │
│ (Flask + Jinja) │
└─────────────────┘


**Flow:**
1. Implant registers once → receives a unique AES key
2. Implant beacons every ~5s (with jitter) → server returns encrypted task queue
3. Implant executes tasks → posts encrypted results back
4. Operator manages everything from the browser dashboard

---

## 🚀 Quickstart

### Requirements
- Python 3.9+
- Linux (tested on Kali)
- Two terminals (one for server, one for implant)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/flask-c2-framework.git
cd flask-c2-framework
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
