# summerslam-watcher
A tiny Python 3 service that watches the WWE SummerSlam 2025 store page and alerts you by email as soon as any wrestler names you care about show up.

- Site watched: https://store.epic.leapevent.tech/wwe-summerslam/2025

- Alert method: Gmail SMTP (uses an App Password or OAuth2 token)

- Runtime: plain Python or Docker container

- Polling cadence: configurable (default 10 minutes)

## Environment Variables

| Variable                | Purpose                                             | Default        |
| ----------------------- | --------------------------------------------------- | -------------- |
| `NAMES_TO_FIND`         | Comma‑separated list of names to watch for          | Pre‑set list\* |
| `GMAIL_USER`            | Gmail address to send **from** (and default **to**) | **Required**   |
| `GMAIL_PASS`            | Gmail App Password or OAuth2 token                  | **Required**   |
| `GMAIL_TO`              | Override alert recipient                            | `GMAIL_USER`   |
| `POLL_INTERVAL_MINUTES` | How often to re‑scan the page (float)               | `10`           |


## Quick Start (local)

```bash
git clone https://github.com/yourname/summerslam-watcher.git
cd summerslam-watcher
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export NAMES_TO_FIND="Chelsea Green,Becky Lynch"
export GMAIL_USER="you@gmail.com"
export GMAIL_PASS="your_app_password"
export POLL_INTERVAL_MINUTES=5

python watcher.py
```

## Run in Docker
Build the image:

```bash
docker build -t summerslam-watcher .
```

Launch the container:

```bash
docker run --rm \
  -e NAMES_TO_FIND="Chelsea Green" \
  -e GMAIL_USER="you@gmail.com" \
  -e GMAIL_PASS="your_app_password" \
  -e POLL_INTERVAL_MINUTES=10 \
  summerslam-watcher
```

