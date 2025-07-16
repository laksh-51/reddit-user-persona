import praw
import re
import os
from dotenv import load_dotenv
from collections import defaultdict
from textblob import TextBlob


load_dotenv()


reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def extract_username(profile_url):
    """Extract username from full Reddit profile URL"""
    match = re.search(r'reddit\.com/user/([^/]+)/?', profile_url)
    return match.group(1) if match else None

def fetch_user_data(username, limit=100):
    user = reddit.redditor(username)
    posts = []
    comments = []

    print(f"Fetching submissions for u/{username}")
    for submission in user.submissions.new(limit=limit):
        posts.append({
            'title': submission.title,
            'body': submission.selftext,
            'url': f"https://reddit.com{submission.permalink}"
        })

    print(f"Fetching comments for u/{username}")
    for comment in user.comments.new(limit=limit):
        comments.append({
            'body': comment.body,
            'url': f"https://reddit.com{comment.permalink}"
        })

    return posts, comments


def analyze_texts(posts, comments):
    persona = defaultdict(list)
    citations = defaultdict(list)

    all_data = [(p['title'] + "\n" + p['body'], p['url']) for p in posts]
    all_data += [(c['body'], c['url']) for c in comments]

    for text, url in all_data:
        lowered = text.lower()

        
        interest_matches = re.findall(r"(?:i like|i love|i enjoy|i'm into)\s+([a-zA-Z0-9\- ]+)", lowered)
        for interest in interest_matches:
            interest_clean = interest.strip().rstrip('.!')
            persona['Interests'].append(interest_clean)
            citations['Interests'].append((interest_clean, url))

        
        if re.search(r"\b(i work as|i am a|i’m a|my job is|i work in)\b", lowered):
            match = re.search(r"(i work as|i am a|i’m a|my job is|i work in)\s+([a-zA-Z ]+)", lowered)
            if match:
                occupation = match.group(2).strip()
                persona['Occupation'].append(occupation)
                citations['Occupation'].append((occupation, url))

        if 'student' in lowered or 'studying' in lowered:
            persona['Occupation'].append("Student")
            citations['Occupation'].append(("Student", url))

        
        age_match = re.search(r"\b(i am|i'm)\s+(\d{2})\b", lowered)
        if age_match:
            age = f"{age_match.group(2)} years old"
            persona['Age'].append(age)
            citations['Age'].append((age, url))

        
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.3:
            sentiment = "Generally Positive"
        elif polarity < -0.3:
            sentiment = "Generally Negative"
        else:
            sentiment = "Neutral / Mixed"
        persona['Personality'].append(sentiment)
        citations['Personality'].append((f"Sentiment score: {polarity:.2f}", url))

        
        word_count = len(text.split())
        style = "Detailed / Verbose" if word_count > 50 else "Concise / Brief"
        persona['Language Style'].append(style)
        citations['Language Style'].append((f"{word_count} words", url))

    
    for k in persona:
        persona[k] = list(set(persona[k]))

    return persona, citations

def write_persona_to_file(username, persona, citations):
    filename = f"{username}_persona.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"USER PERSONA FOR: u/{username}\n\n")
        for trait, values in persona.items():
            f.write(f"{trait}:\n")
            for val in values:
                f.write(f" - {val}\n")
                for v, cite_url in citations[trait]:
                    if v == val:
                        f.write(f"   ➤ Cited from: https://reddit.com{cite_url}\n")
            f.write("\n")
    print(f"[✓] Persona written to {filename}")


if __name__ == "__main__":
    profile_url = input("Enter Reddit user profile URL: ").strip()
    username = extract_username(profile_url)

    if username:
        posts, comments = fetch_user_data(username)
        persona, citations = analyze_texts(posts, comments)
        write_persona_to_file(username, persona, citations)
    else:
        print("Invalid Reddit user URL.")

