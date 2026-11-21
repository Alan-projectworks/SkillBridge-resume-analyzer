from skill_matcher import match_skills

resume = """
Python developer with SQL and ReactJS experience.
"""

job = """
We need a Python developer with skills in
Python, SQL, React.js and communication.
"""

result = match_skills(resume, job)

print(result)