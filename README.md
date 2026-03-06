# ieee-xplore-tracker

Automated daily IEEE Xplore paper tracker for Android using Termux and Tasker.

Fetches new papers by keyword every morning, saves a dated HTML report, and sends a notification. Tap to open — links go directly to IEEE Xplore.

---

## How It Works

1. Tasker triggers the script at 09:00 every day
2. `tracker.py` reads keywords from `config.json` and queries the IEEE Xplore API
3. Results are saved as a dated HTML report (`results/YYYY-MM-DD.html`)
4. A notification is sent — tap it to open the report in your browser
5. Reports older than 7 days are automatically deleted

---

## Requirements

- [Termux](https://f-droid.org/packages/com.termux/)
- [Termux:API](https://f-droid.org/packages/com.termux.api/)
- [Termux:Tasker](https://f-droid.org/packages/com.termux.tasker/)
- [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm)
- Python 3 + `requests` library
- IEEE Xplore API key — free at [developer.ieee.org](https://developer.ieee.org)

---

## Setup

### 1. Install Python dependencies

```bash
pip install requests
```

### 2. Clone the repo

```bash
git clone https://github.com/1337leets/ieee-xplore-tracker
cd ieee-xplore-tracker
```

### 3. Configure

Edit `config.json`:

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "keywords": [
    "hydrogen microgrid",
    "real-time simulation HIL",
    "microgrid energy management"
  ],
  "max_results": 5,
  "days_back": 1,
  "keep_days": 7
}
```

| Field | Description |
|---|---|
| `api_key` | Your IEEE Xplore API key |
| `keywords` | List of search terms |
| `max_results` | Max papers per keyword per day |
| `days_back` | How many days back to search |
| `keep_days` | How many daily reports to keep |

### 4. Test manually

```bash
python tracker.py
```

### 5. Set up Tasker

**Option A — Import (recommended):**

A ready-to-use Tasker profile is included: `ieee_tracker_tasker.xml`

In Tasker: Long press on Profiles → Import → select the file.

**Option B — Manual:**

1. Create a new **Profile** → **Time** → From: `09:00`, To: `09:01`
2. Create a new **Task** → **Plugin** → **Termux:Tasker**
3. Set:
   - **Executable:** `/data/data/com.termux/files/usr/bin/python3`
   - **Arguments:** `/data/data/com.termux/files/home/ieee-xplore-tracker/tracker.py`
   - **Working directory:** `/data/data/com.termux/files/home/ieee-xplore-tracker`
   - **Timeout:** 60 seconds
4. Link the task to the profile

---

## Notes

- The `results/` directory is created automatically on first run
- Internet and Termux must be available at trigger time
- IEEE Xplore API keys are activated during business hours (8am–5pm ET, Mon–Fri)
- API rate limit: 200 calls/day — well within daily usage
- If no papers are found for a keyword, the HTML report will show "No results found" for that section — not an error

---

## Known Limitations

- Termux must be running or allowed to start in the background at trigger time — behavior may vary by Android version and battery optimization settings
- If the API key is not yet activated, the script will exit early with a message in stdout
- `termux-notification` tap action opens the HTML file using the system default browser; behavior may vary across devices

---

## Status

Tested on: Android 10, Termux 0.118, Python 3.11  
API key activation and full end-to-end notification flow pending final test.

---

## License

MIT
