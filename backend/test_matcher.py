from skill_matcher import match_skills
import json

resume = """
John Doe
Senior Software Engineer with 4 years experience in Python, Django, REST APIs, PostgreSQL, and JavaScript.
Built scalable microservices, integrated Redis caching, and managed deployment workflows with Docker and Git.
Hands-on with HTML5, CSS3, and unit testing using PyTest. Strong team communication and agile collaboration.
"""

job = """
We are seeking a Full Stack Engineer to join our core product team.
Key Requirements:
- Must have 3+ years experience in Python and FastAPI.
- Required: React, TypeScript, and modern Frontend Development.
- Essential: PostgreSQL or relational SQL database design.
- Hands-on experience with Docker and Kubernetes is a strong plus.
- Excellent communication skills and problem solving ability.
- Nice to have: Machine Learning experience with PyTorch.
"""

result = match_skills(resume, job)

print("=== MATCH ANALYSIS TEST ===")
print("Match Score:", result["match_percentage"])
print("Matched Skills:", result["matched_skills"])
print("Partial Skills:", result["partial_skills"])
print("Missing Skills:", result["missing_skills"])
print("Top 3 Priorities:", [p["skill"] + f" ({p['priority']})" for p in result["skill_priorities"]])
print("AI Summary:", result["ai_summary"])
print("Career Recommendations:", [r["title"] + f" ({r['match_score']}%)" for r in result["career_recommendations"]])
print("Learning Plan Days:", len(result["learning_plan"]))
assert len(result["learning_plan"]) == 7, "Roadmap should have 7 days"
print("TEST PASSED SUCCESSFULLY!")
