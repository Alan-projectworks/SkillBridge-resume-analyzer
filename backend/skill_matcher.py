
"""Skill matching engine for SkillBridge."""

import re

SKILL_ALIASES = {
    "python": ["python", "python3"],
    "sql": ["sql", "mysql", "postgresql", "sqlite", "postgres"],
    "react.js": ["react.js", "reactjs", "react js"],
    "javascript": ["javascript", "java script"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "fastapi": ["fastapi", "fast api"],
    "django": ["django"],
    "machine learning": ["machine learning", "ml"],
    "communication": [
        "communication",
        "communication skills",
        "verbal communication",
        "written communication"
    ],
    "git": ["git", "github"],
    "java": ["java"],
    "c++": ["c++"],
    "node.js": ["node.js", "nodejs", "node js"],
}


def normalize_text(text):
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_skill(text, aliases):
    for alias in aliases:
        pattern = (
            r"(?<!\w)"
            + re.escape(alias.lower())
            + r"(?!\w)"
        )

        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def extract_skills(text):
    normalized = normalize_text(text)

    found_skills = []

    for skill, aliases in SKILL_ALIASES.items():
        if contains_skill(normalized, aliases):
            found_skills.append(skill)

    return found_skills


def match_skills(resume_text, job_description):

    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    total = len(required_skills)

    match_percentage = (
        round(len(matched_skills) / total * 100, 2)
        if total else 0
    )

    missing_skill_details = []

    original_lines = job_description.splitlines()

    for skill in missing_skills:
        aliases = SKILL_ALIASES[skill]

        matching_lines = [
            line.strip()
            for line in original_lines
            if contains_skill(normalize_text(line), aliases)
            and line.strip()
        ]

        missing_skill_details.append({
            "skill": skill,
            "reason": (
                "Required by the job description "
                "but not found in your resume."
            ),
            "job_description_lines": matching_lines
        })

    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "missing_skill_details": missing_skill_details,
        "match_percentage": match_percentage
    }
