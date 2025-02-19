# Orbit Simple Monitor (OSM) 🚀🪐

**Orbit Simple Monitor (OSM)** is a **lightweight** host-level monitoring tool that measures **CPU, RAM, and DISK** usage of a **Linux Docker host**, logs them in **SQLite**, and sends **Slack/Email** alerts if thresholds are exceeded! Made with ❤️ in Senegal.

<img src="./assets/OSM-COVER.jpg" alt="Orbit Simple Monitor" width="100%" center/>

<br/>

## 🌟 Features

- **CPU/RAM/DISK** usage collection at configurable intervals (seconds/minutes/hours).  
- **Automatic daily cleanup** of historical data (older than 30 days).  
- **SQLite** for persistence, rotating logs (`osm.log`), and real-time console logs.  
- **Slack & Email alerts** when thresholds exceed your chosen limits.  

<br/>

## 🚀 Quick Start (Docker)

### 1) **Linux-Host Only** 🤖🐧

> **Important**: This container relies on **`/proc`** from the **Linux** host for accurate metrics.  
> It **will fail** on Windows hosts because **`/proc`** does **not** exist on Windows.  

### 2) **Pull & Run**

## 🛠 Example: Docker Compose

You can also run OSM with your own **`docker-compose.yml`**:

```yaml
version: '3.8'
services:
  osm:
    image: orbitturner/orbit-simple-monitor:latest
    container_name: osm-monitor
    environment:
      YOUR_SERVER_NAME: "Sama Server"
      DB_FILE: "/data/osm.db"
      CPU_THRESHOLD: 80
      RAM_THRESHOLD: 80
      DISK_THRESHOLD: 80
      CHECK_INTERVAL: 1
      CHECK_INTERVAL_UNIT: "m"
      SLACK_WEBHOOK_URL: "https://hooks.slack.com/services/XXX/YYY/ZZZ"
      ALERT_EMAIL: "alerts@example.com"
      SMTP_SERVER: "smtp.example.com"
      SMTP_PORT: 587
      SMTP_USER: "user@example.com"
      SMTP_PASS: "secret"
      ALERT_CHANNELS: "SLACK,EMAIL"
    volumes:
      - ./osm_data:/data
      # For host-level monitoring on Linux, mount /proc:
      - /proc:/host_proc:ro
    restart: unless-stopped
```

Then:
```bash
docker-compose up -d
docker-compose logs -f
```


```bash
docker pull orbitturner/orbit-simple-monitor:latest

docker run --rm \
  -it \
  -e YOUR_SERVER_NAME="Sama Server" \
  -e DB_FILE="/data/osm.db" \
  -e CPU_THRESHOLD=80 \
  -e RAM_THRESHOLD=80 \
  -e DISK_THRESHOLD=80 \
  -e CHECK_INTERVAL=1 \
  -e CHECK_INTERVAL_UNIT="m" \
  -e SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ" \
  -e ALERT_EMAIL="alerts@example.com" \
  -e SMTP_SERVER="smtp.example.com" \
  -e SMTP_PORT=587 \
  -e SMTP_USER="user@example.com" \
  -e SMTP_PASS="secret" \
  -e ALERT_CHANNELS="SLACK,EMAIL" \
  --mount type=bind,source="$(pwd)/osm_data",target=/data \
  --mount type=bind,source=/proc,target=/host_proc,readonly \
  orbitturner/orbit-simple-monitor:latest
```

- **`-it`**: For interactive mode to see logs in real-time.
- **Mounting `/proc`** from the Linux host to `/host_proc` inside the container.  
- **Mounting `osm_data/`** on your host to `/data` for persistent DB & logs.

---

## 📝 Environment Variables

| Variable             | Default              | Description                                                                                          |
|----------------------|----------------------|------------------------------------------------------------------------------------------------------|
| **`YOUR_SERVER_NAME`**   | `SamaServerBouNeikhBi` | Friendly name displayed in alerts.                                                                    |
| **`DB_FILE`**            | `osm.db`              | Path to the SQLite database file.                                                                     |
| **`CPU_THRESHOLD`**      | `90`                  | CPU usage threshold (%) to trigger alerts.                                                            |
| **`RAM_THRESHOLD`**      | `90`                  | RAM usage threshold (%) to trigger alerts.                                                            |
| **`DISK_THRESHOLD`**     | `90`                  | Disk usage threshold (%) to trigger alerts.                                                           |
| **`CHECK_INTERVAL`**     | `1`                   | Numeric interval for metric collection.                                                               |
| **`CHECK_INTERVAL_UNIT`**| `m`                   | Interval unit: **`s`** (seconds), **`m`** (minutes), **`h`** (hours).                                 |
| **`SLACK_WEBHOOK_URL`**  | (empty)              | If set, sends Slack alerts to this webhook.                                                           |
| **`ALERT_EMAIL`**        | `alerts@example.com`  | Email address for sending alerts.                                                                     |
| **`SMTP_SERVER`**        | `smtp.example.com`    | SMTP server for sending emails.                                                                       |
| **`SMTP_PORT`**          | `587`                 | SMTP port.                                                                                            |
| **`SMTP_USER`**          | `user@example.com`    | SMTP username.                                                                                        |
| **`SMTP_PASS`**          | `secret`              | SMTP password.                                                                                        |
| **`ALERT_CHANNELS`**     | `SLACK,EMAIL`         | Comma-separated channels: `SLACK`, `EMAIL`, or `SLACK,EMAIL`.                                         |

---


> **Note**: This **only** works on **Linux**. Windows does not have `/proc`, so host-level metrics won't function.

---

## 👩‍💻 Developer Guide

### 1) Run Locally (No Docker)

1. **Clone** this repo:
   ```bash
   git clone https://github.com/orbitturner/orbit-simple-monitor.git
   cd orbit-simple-monitor
   ```
2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run**:
   ```bash
   python osm.py
   ```
   Logs appear in **stdout** and in `osm.log`.

### 2) Run Tests

```bash
pip install pytest
pytest
```

If everything passes, you’re good to go!

### 3) Build & Push Docker Image

1. **Build**:
   ```bash
   docker build -t osm-monitor .
   ```
2. **Tag**:
   ```bash
   docker tag osm-monitor orbitturner/orbit-simple-monitor:latest
   ```
3. **Push**:
   ```bash
   docker push orbitturner/orbit-simple-monitor:latest
   ```

Now your image is available on Docker Hub. 🏆

---

## ⚠️ Platform Note

- **Linux**: Fully supported. Just make sure to mount `/proc:/host_proc:ro` if you want full **host-level** stats.  
- **Windows**: Currently, no `/proc` -> **OSM** will **not** collect host metrics. It may run but will fail or produce partial data.  
- **macOS**: Similar limitation for host-level monitoring with Docker; it’s geared for Linux.  

---

## 💬 Community & Support

- **Issues** / **Pull Requests**: Are welcome!  
- **Slack / Email**: For questions or alerts.  

🚀 **Thank you** for using **Orbit Simple Monitor** to watch your server’s resources from Earth’s orbit! 🌍🪐🌌  

---
**Made with ❤️ in Senegal**.  