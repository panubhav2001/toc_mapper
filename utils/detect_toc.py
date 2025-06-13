import os
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv

# Load .env from outer folder
dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOC_KEYWORDS = ["table of contents", "contents", "index", "content", "toc"]

def is_toc_page_llm(page_text, model="llama-3.3-70b-versatile"):
    """
    Uses Groq LLM to classify whether a page is a TOC page.
    """
    prompt = f"""
You are a PDF assistant. Determine if the following page is part of the Table of Contents.

Answer with only one word: "Yes" or "No".

Text:
\"\"\"{page_text.strip()[:3000]}\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith("yes")
    except Exception as e:
        print(f"Groq API error on page: {e}")
        return False

def has_toc_keywords(text: str) -> bool:
    """
    Simple keyword check to avoid unnecessary LLM calls.
    """
    lowered = text.lower()
    return any(keyword in lowered for keyword in TOC_KEYWORDS)

def find_toc_page(pages):
    """
    Identifies the start and end TOC pages using Groq LLM,
    but only processes pages with likely TOC keywords.
    """
    start_page = None
    end_page = None
    started = False

    for page_num in sorted(pages.keys()):
        text = pages[page_num]

        if not has_toc_keywords(text):
            continue  # skip pages with no keywords

     #   print(f"[LLM] Analyzing page {page_num}...")
        is_toc = is_toc_page_llm(text)

        if is_toc:
            if not started:
                start_page = page_num
                started = True
            end_page = page_num
        else:
            if started:
                break  # TOC sequence ended

    return start_page, end_page
