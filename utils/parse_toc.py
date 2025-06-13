import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_toc_entries(text):
    prompt = f"""
You are a table of contents parser.

From the given raw TOC text, extract only a Python list of (title, page_number) tuples.

- Do not modify Roman numeral page numbers (e.g., "xvii", "xxiii").
- Titles may include numbering or formatting. Preserve them.
- No explanations or markdown. Return only the Python list.

Example:

Input:
Preface    xvii  
About the Authors    xxiii

Output:
[("Preface", "xvii"), ("About the Authors", "xxiii")]

Now extract from this TOC text:
{text}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You convert raw TOC text into structured (title, page_number) pairs."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()
    # print(content)
    try:
        entries = eval(content)
        if isinstance(entries, list) and all(isinstance(x, tuple) and isinstance(x[1], (int, str)) for x in entries):
            return entries
        else:
            raise ValueError("Invalid format from LLM.")
    except Exception as e:
        print("Error parsing LLM response:", e)
        return []
