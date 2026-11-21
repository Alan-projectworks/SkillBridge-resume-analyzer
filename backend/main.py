
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz
from skill_matcher import match_skills



# DYNAMIC 14-DAY LEARNING PLAN GENERATOR


def generate_learning_plan(missing_skills):
    skill_topics = {
        "c++": [
            ("C++ fundamentals", "Practice variables, data types and operators."),
            ("Conditions", "Write programs using if, else and switch."),
            ("Loops", "Build multiplication tables using loops."),
            ("Functions", "Create reusable functions for calculations."),
            ("Arrays", "Find the largest and smallest array elements."),
            ("Strings", "Build a string manipulation program."),
            ("Pointers", "Practice pointers and memory addresses."),
            ("References", "Understand references and pass-by-reference."),
            ("Object-oriented programming", "Create classes and objects."),
            ("Constructors", "Implement constructors and destructors."),
            ("Inheritance", "Build a simple inheritance example."),
            ("Polymorphism", "Practice function overriding and overloading."),
            ("STL", "Practice vectors, maps and sorting."),
            ("Final project", "Build a student management system in C++.")
        ],
        "python": [
            ("Python fundamentals", "Practice variables, data types and operators."),
            ("Conditions", "Write programs using conditional statements."),
            ("Loops", "Solve problems using for and while loops."),
            ("Functions", "Create reusable Python functions."),
            ("Lists and tuples", "Build a program to manage student marks."),
            ("Dictionaries and sets", "Create a contact book."),
            ("Strings", "Practice string manipulation."),
            ("File handling", "Read and write text files."),
            ("Exception handling", "Handle invalid user input."),
            ("Modules", "Organize code using Python modules."),
            ("OOP", "Create classes and objects."),
            ("Libraries", "Explore useful Python libraries."),
            ("Practice project", "Build a small Python application."),
            ("Final project", "Create a complete Python mini-project.")
        ],
        "sql": [
            ("SQL fundamentals", "Practice SELECT and DISTINCT."),
            ("Filtering", "Use WHERE, AND, OR and LIKE."),
            ("Sorting", "Practice ORDER BY and LIMIT."),
            ("Aggregate functions", "Use COUNT, SUM, AVG, MIN and MAX."),
            ("Grouping", "Practice GROUP BY and HAVING."),
            ("Joins", "Understand INNER JOIN and LEFT JOIN."),
            ("Subqueries", "Write queries using nested SELECT."),
            ("Database design", "Create tables with primary keys."),
            ("Constraints", "Practice foreign keys and constraints."),
            ("Data modification", "Use INSERT, UPDATE and DELETE."),
            ("Views", "Create and query database views."),
            ("Indexes", "Understand database indexing."),
            ("Query practice", "Solve real-world SQL problems."),
            ("Final project", "Design and query a small database.")
        ],
        "react": [
            ("React fundamentals", "Understand React and component structure."),
            ("JSX", "Create reusable JSX components."),
            ("Props", "Pass data between components."),
            ("State", "Practice useState."),
            ("Events", "Handle clicks and form events."),
            ("Conditional rendering", "Display content based on conditions."),
            ("Lists", "Render arrays using map."),
            ("Forms", "Build a controlled form."),
            ("useEffect", "Understand React effects."),
            ("API integration", "Fetch data from an API."),
            ("Routing", "Explore React Router."),
            ("Component design", "Create reusable UI components."),
            ("Project practice", "Build a small React application."),
            ("Final project", "Create a complete React mini-project.")
        ],
        "react.js": [
            ("React fundamentals", "Understand React and component structure."),
            ("JSX", "Create reusable JSX components."),
            ("Props", "Pass data between components."),
            ("State", "Practice useState."),
            ("Events", "Handle clicks and form events."),
            ("Conditional rendering", "Display content based on conditions."),
            ("Lists", "Render arrays using map."),
            ("Forms", "Build a controlled form."),
            ("useEffect", "Understand React effects."),
            ("API integration", "Fetch data from an API."),
            ("Routing", "Explore React Router."),
            ("Component design", "Create reusable UI components."),
            ("Project practice", "Build a small React application."),
            ("Final project", "Create a complete React mini-project.")
        ],
        "javascript": [
            ("JavaScript fundamentals", "Practice variables and data types."),
            ("Operators and conditions", "Write conditional programs."),
            ("Loops", "Solve problems using loops."),
            ("Functions", "Create reusable functions."),
            ("Arrays", "Practice array methods."),
            ("Objects", "Create and manipulate objects."),
            ("DOM", "Select and update HTML elements."),
            ("Events", "Handle browser events."),
            ("ES6", "Explore arrow functions and destructuring."),
            ("Promises", "Understand asynchronous JavaScript."),
            ("Async and await", "Fetch data asynchronously."),
            ("JSON", "Parse and manipulate JSON data."),
            ("Project practice", "Build an interactive webpage."),
            ("Final project", "Create a complete JavaScript application.")
        ]
    }

    if not missing_skills:
        return []

    plan = []
    selected_skills = missing_skills[:3]

    for item in selected_skills:
        skill = (
            item if isinstance(item, str)
            else item.get("skill", "Unknown skill")
        )
        normalized = skill.lower().strip()
        topics = skill_topics.get(normalized)

        if topics is None:
            topics = [
                (f"{skill} fundamentals", f"Learn the basic concepts of {skill}."),
                (f"{skill} core concepts", f"Study the important concepts of {skill}."),
                (f"{skill} terminology", f"Understand commonly used {skill} terminology."),
                (f"{skill} practical examples", f"Follow practical {skill} examples."),
                (f"{skill} beginner exercises", f"Solve beginner exercises using {skill}."),
                (f"{skill} intermediate concepts", f"Explore intermediate {skill} concepts."),
                (f"{skill} problem solving", f"Solve problems using {skill}."),
                (f"{skill} practical applications", f"Explore real-world applications of {skill}."),
                (f"{skill} advanced practice", f"Practice more advanced {skill} concepts."),
                (f"{skill} mini project", f"Build a small project using {skill}."),
                (f"{skill} debugging", f"Identify and fix common {skill} errors."),
                (f"{skill} best practices", f"Learn best practices for using {skill}."),
                (f"{skill} revision", f"Revise the important concepts of {skill}."),
                (f"{skill} final project", f"Complete a practical project using {skill}.")
            ]

        plan.append({
            "skill": skill,
            "topics": topics
        })

    daily_plan = []
    for day in range(14):
        skill_index = min(
            day * len(plan) // 14,
            len(plan) - 1
        )
        selected = plan[skill_index]
        topic_index = min(
            day * len(selected["topics"]) // 14,
            len(selected["topics"]) - 1
        )
        topic, task = selected["topics"][topic_index]
        daily_plan.append({
            "day": day + 1,
            "skill": selected["skill"],
            "topic": topic,
            "task": task
        })

    return daily_plan


app = FastAPI(title="SkillBridge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to SkillBridge API!",
        "status": "running"
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is empty."
        )

    content = await resume.read(5 * 1024 * 1024 + 1)

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Resume exceeds 5 MB."
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    try:
        pdf_document = fitz.open(
            stream=content,
            filetype="pdf"
        )

        if pdf_document.needs_pass:
            raise HTTPException(
                status_code=400,
                detail="Password-protected PDFs are not supported."
            )

        extracted_text = ""

        for page in pdf_document:
            extracted_text += page.get_text("text") + "\n"

        page_count = len(pdf_document)
        pdf_document.close()

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF file."
        )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found. This PDF may be scanned."
        )

    analysis = match_skills(
        extracted_text,
        job_description
    )

    # Generate a personalized learning plan
    missing_skills = analysis.get(
        "missing_skill_details",
        []
    )
    learning_plan = generate_learning_plan(missing_skills)
    analysis["learning_plan"] = learning_plan

    return {
        "success": True,
        "message": "Resume analyzed successfully!",
        "filename": resume.filename,
        "page_count": page_count,
        "analysis": analysis
    }
