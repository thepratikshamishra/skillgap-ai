from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_roadmap(target_role, readiness_score, current_skills, critical_gaps):

    prompt = f"""
You are an expert career mentor.

Target Role:
{target_role}

Current Readiness Score:
{readiness_score}%

Current Skills:
{", ".join(current_skills)}

Critical Skill Gaps:
{", ".join(critical_gaps)}

Create a realistic week-by-week learning roadmap.

Requirements:
1. Prioritize the critical skill gaps first.
2. Focus on one or two skills at a time.
3. Include weekly goals.
4. Include practice exercises.
5. Include mini projects.
6. Include a final capstone project.
7. Keep the roadmap practical and beginner-friendly.
8. Use clear headings and bullet points.

Return only the roadmap.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def extract_skills_from_resume(resume_text):
    """
    Use Llama 3 to extract a clean list of technical skills from resume text.
    Returns a Python list of skill strings.
    """

    prompt = f"""
You are a resume parser.

Below is the text extracted from a candidate's resume.
Your job is to extract ONLY the technical skills mentioned anywhere in the resume.

Rules:
- Include programming languages, frameworks, tools, libraries, platforms, databases.
- Do NOT include soft skills like "communication", "teamwork", "leadership".
- Do NOT include job titles, company names, or degrees.
- Return ONLY a valid JSON array of skill strings, nothing else.
- No explanation, no markdown, no backticks. Just the raw JSON array.

Example output:
["Python", "SQL", "Pandas", "Power BI", "Excel"]

Resume text:
{resume_text[:4000]}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()

    # Clean up in case model wraps in backticks
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        skills = json.loads(raw)
        if isinstance(skills, list):
            return [str(s).strip() for s in skills if s]
    except json.JSONDecodeError:
        pass

    # Fallback: try to find anything that looks like a list
    match = re.search(r'\[.*?\]', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    # Last resort: split by comma
    return [s.strip().strip('"') for s in raw.split(",") if s.strip()]