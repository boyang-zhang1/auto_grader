# Moodle Auto Grader

Automate the grading process for Moodle essay questions. Fetches submissions, displays them efficiently, and submits grades back to Moodle.

## Features

- Automated fetching of submissions requiring grading
- Smart grouping by question slot
- Question deduplication (shows question text only once)
- Progress tracking
- Secure configuration via `.env` file

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Moodle credentials
```

### Getting Moodle Cookies

1. Log into Moodle and navigate to your quiz report page
2. Open Developer Tools (F12) → Network tab → Refresh page
3. Click first request → Find "Cookie:" header → Copy entire value
4. Paste into `.env` as `MOODLE_COOKIES`

### Usage

```bash
python auto_grader.py
```

The tool will:
1. Fetch all submissions requiring grading
2. Display question and student answers
3. Prompt for grades
4. Submit to Moodle

## Configuration

Edit `.env`:

```env
MOODLE_BASE_URL=https://moodle.lsu.edu
QUIZ_REPORT_URL=https://moodle.lsu.edu/mod/quiz/report.php?id=YOUR_QUIZ_ID&mode=overview
MOODLE_COOKIES=your_cookies_here
```

## Project Structure

```
auto_grader/
├── .env              # Your private config (git-ignored)
├── config.py         # Configuration management
├── moodle_client.py  # Moodle API client
├── auto_grader.py    # Main entry point
└── requirements.txt  # Dependencies
```

## Troubleshooting

**No questions found?** Check your `QUIZ_REPORT_URL` and ensure submissions exist.

**Grade submission failed?** Your cookies may be expired. Get fresh cookies and update `.env`.

**Question/Answer not found?** Cookies expired or page structure changed. Refresh cookies.

## Security

- Never commit `.env` - it contains authentication data
- Cookies expire periodically - refresh as needed
- Only grade submissions you have permission to access

## License

MIT License - Use and modify as needed.

## Disclaimer

Use responsibly and ethically. Comply with your institution's policies and protect student privacy.
