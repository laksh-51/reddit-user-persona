# Reddit User Persona Generator

This Python project extracts Reddit user data to build a basic user persona based on their posts and comments.

##  Features
- Takes Reddit user profile URL as input
- Scrapes recent posts and comments using Reddit API
- Analyzes text to infer:
  - Interests
  - Occupation / Student
  - Age (if available)
  - Personality (via sentiment)
  - Language style
- Generates a `.txt` user persona report with **citations** for each insight

---

##  Technologies Used
- Python 3.x
- `praw` (Reddit API)
- `textblob` (Sentiment Analysis)
- `re` (Regex for trait extraction)
- `dotenv` (optional)

---

##  Setup Instructions

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/reddit-user-persona.git
cd reddit-user-persona
