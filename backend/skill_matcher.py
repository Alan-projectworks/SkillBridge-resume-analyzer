"""Skill matching and career intelligence engine for Skillora (SkillBridge 2.0).

Provides:
- Contextual resume & job description skill extraction
- Disambiguation and synonym normalization (e.g. ReactJS -> React, ML -> Machine Learning)
- Exact, partial, and missing skill classification
- Resume evidence sentence extraction
- Job description line and priority extraction (High, Medium, Low)
- Explainable skill gap analysis
- 7-day personalized actionable sprint roadmap
- Career recommendations based on actual resume skills
- Category distribution for visual analytics
- Dynamic executive summary synthesis
"""

import re
from typing import Dict, List, Any, Tuple, Optional

# ============================================================================
# SKILL TAXONOMY AND NORMALIZATION DICTIONARY
# ============================================================================

SKILL_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # --- Frontend Development ---
    "React": {
        "category": "Frontend Development",
        "aliases": ["react", "react.js", "reactjs", "react js"],
        "foundations": ["JavaScript", "HTML", "CSS", "TypeScript", "Vue.js"],
        "transfer_note": "Foundations in JavaScript and modern UI components provide a direct pathway to mastering React."
    },
    "JavaScript": {
        "category": "Frontend Development",
        "aliases": ["javascript", "js", "ecmascript", "es6", "es2015"],
        "foundations": ["TypeScript", "HTML", "Python"],
        "transfer_note": "Demonstrated scripting and language mechanics make acquiring JavaScript syntax straightforward."
    },
    "TypeScript": {
        "category": "Frontend Development",
        "aliases": ["typescript", "ts"],
        "foundations": ["JavaScript", "Java", "C#"],
        "transfer_note": "Solid JavaScript fluency combined with typed OOP concepts translates directly into TypeScript type annotations and generics."
    },
    "HTML": {
        "category": "Frontend Development",
        "aliases": ["html", "html5", "semantic html"],
        "foundations": ["Frontend Development", "CSS", "Web Development"],
        "transfer_note": "Web presentation fundamentals align with HTML semantic markup."
    },
    "CSS": {
        "category": "Frontend Development",
        "aliases": ["css", "css3", "stylesheets"],
        "foundations": ["HTML", "Tailwind CSS", "Bootstrap"],
        "transfer_note": "UI styling experience transfers easily to CSS layout engines like Flexbox and Grid."
    },
    "Tailwind CSS": {
        "category": "Frontend Development",
        "aliases": ["tailwind", "tailwind css", "tailwindcss"],
        "foundations": ["CSS", "HTML", "Bootstrap"],
        "transfer_note": "Understanding CSS box model and utility styling makes Tailwind CSS rapid to adopt."
    },
    "Vue.js": {
        "category": "Frontend Development",
        "aliases": ["vue", "vue.js", "vuejs"],
        "foundations": ["JavaScript", "React", "HTML"],
        "transfer_note": "Component-based architecture experience in React or vanilla JS accelerates Vue.js onboarding."
    },
    "Angular": {
        "category": "Frontend Development",
        "aliases": ["angular", "angularjs", "angular 2+"],
        "foundations": ["TypeScript", "JavaScript", "React"],
        "transfer_note": "Familiarity with TypeScript and single-page application patterns provides strong foundations for Angular."
    },
    "Next.js": {
        "category": "Frontend Development",
        "aliases": ["next.js", "nextjs", "next js"],
        "foundations": ["React", "JavaScript", "Node.js"],
        "transfer_note": "React component architecture forms the exact basis of Next.js server-side and client rendering."
    },
    "Redux": {
        "category": "Frontend Development",
        "aliases": ["redux", "redux toolkit", "rtk"],
        "foundations": ["React", "JavaScript"],
        "transfer_note": "Experience with frontend state flow and immutable patterns makes Redux concepts easy to grasp."
    },

    # --- Backend & APIs ---
    "Python": {
        "category": "Backend & APIs",
        "aliases": ["python", "python3", "py"],
        "foundations": ["Java", "C++", "JavaScript", "Backend Development"],
        "transfer_note": "Strong programming fundamentals enable quick proficiency with Python syntax and data structures."
    },
    "FastAPI": {
        "category": "Backend & APIs",
        "aliases": ["fastapi", "fast api"],
        "foundations": ["Python", "Flask", "Django", "REST APIs"],
        "transfer_note": "Demonstrated Python experience and RESTful design knowledge directly map to FastAPI development."
    },
    "Django": {
        "category": "Backend & APIs",
        "aliases": ["django", "django rest framework", "drf"],
        "foundations": ["Python", "Flask", "FastAPI", "SQL"],
        "transfer_note": "Proficiency in Python and MVC patterns allows immediate acclimation to Django's batteries-included model."
    },
    "Flask": {
        "category": "Backend & APIs",
        "aliases": ["flask"],
        "foundations": ["Python", "FastAPI", "Django"],
        "transfer_note": "Python web routing and request-response handling map directly into Flask."
    },
    "Node.js": {
        "category": "Backend & APIs",
        "aliases": ["node.js", "nodejs", "node js", "node"],
        "foundations": ["JavaScript", "TypeScript", "Backend Development", "Express.js"],
        "transfer_note": "JavaScript expertise provides the core runtime knowledge for asynchronous Node.js servers."
    },
    "Express.js": {
        "category": "Backend & APIs",
        "aliases": ["express", "express.js", "expressjs"],
        "foundations": ["Node.js", "JavaScript", "REST APIs"],
        "transfer_note": "Node.js fluency and HTTP lifecycle knowledge transfer directly to Express middleware patterns."
    },
    "Java": {
        "category": "Backend & APIs",
        "aliases": ["java", "core java", "j2ee"],
        "foundations": ["C++", "C#", "OOP", "Spring Boot"],
        "transfer_note": "Object-oriented and strongly typed language foundations provide a seamless bridge to Java."
    },
    "Spring Boot": {
        "category": "Backend & APIs",
        "aliases": ["spring boot", "springboot", "spring framework", "spring"],
        "foundations": ["Java", "Backend Development", "REST APIs"],
        "transfer_note": "Core Java mastery and enterprise patterns enable rapid comprehension of Spring dependency injection."
    },
    "C++": {
        "category": "Backend & APIs",
        "aliases": ["c++", "cpp"],
        "foundations": ["C", "Java", "Data Structures", "Algorithms"],
        "transfer_note": "Strong low-level systems logic and algorithmic background facilitate mastering C++ memory control."
    },
    "C#": {
        "category": "Backend & APIs",
        "aliases": ["c#", "csharp", "c sharp", ".net"],
        "foundations": ["Java", "C++", "OOP"],
        "transfer_note": "Object-oriented experience in Java or C++ makes C# and .NET idioms very familiar."
    },
    "Go": {
        "category": "Backend & APIs",
        "aliases": ["go", "golang"],
        "foundations": ["C++", "Python", "Backend Development", "Microservices"],
        "transfer_note": "Compiled language understanding and backend systems design simplify learning Go concurrency and interfaces."
    },
    "REST APIs": {
        "category": "Backend & APIs",
        "aliases": ["rest", "rest api", "rest apis", "restful", "restful apis", "restful api", "web apis"],
        "foundations": ["HTTP", "FastAPI", "Express.js", "Flask", "Backend Development"],
        "transfer_note": "Client-server web development background implies working knowledge of HTTP methods and payloads."
    },
    "GraphQL": {
        "category": "Backend & APIs",
        "aliases": ["graphql", "apollo graphql"],
        "foundations": ["REST APIs", "Node.js", "Backend Development"],
        "transfer_note": "Knowledge of API schema design and endpoint routing provides a strong base for GraphQL queries and resolvers."
    },
    "Microservices": {
        "category": "Backend & APIs",
        "aliases": ["microservices", "microservice architecture", "distributed systems"],
        "foundations": ["REST APIs", "Docker", "Backend Development"],
        "transfer_note": "Modular code design and API-first architectures naturally evolve into microservice decoupling."
    },

    # --- Databases & Storage ---
    "SQL": {
        "category": "Databases & Storage",
        "aliases": ["sql", "structured query language", "relational database", "rdbms"],
        "foundations": ["PostgreSQL", "MySQL", "SQLite", "Database Management"],
        "transfer_note": "Working with any structured data storage builds the logical querying principles of SQL."
    },
    "PostgreSQL": {
        "category": "Databases & Storage",
        "aliases": ["postgresql", "postgres", "psql"],
        "foundations": ["SQL", "MySQL", "SQLite"],
        "transfer_note": "General SQL syntax and indexing principles transfer directly to PostgreSQL features."
    },
    "MySQL": {
        "category": "Databases & Storage",
        "aliases": ["mysql", "mariadb"],
        "foundations": ["SQL", "PostgreSQL", "SQLite"],
        "transfer_note": "Relational table modeling and standard SQL syntax make MySQL straightforward to navigate."
    },
    "MongoDB": {
        "category": "Databases & Storage",
        "aliases": ["mongodb", "mongo", "nosql"],
        "foundations": ["JSON", "JavaScript", "SQL", "Databases"],
        "transfer_note": "Working with JSON data payloads and schema design eases transition to document-oriented MongoDB."
    },
    "Redis": {
        "category": "Databases & Storage",
        "aliases": ["redis", "in-memory cache", "caching"],
        "foundations": ["SQL", "Backend Development", "System Design"],
        "transfer_note": "Backend request handling experience gives clear insight into cache eviction and key-value latency benefits."
    },
    "Elasticsearch": {
        "category": "Databases & Storage",
        "aliases": ["elasticsearch", "elastic search", "elk"],
        "foundations": ["SQL", "MongoDB", "Search Engines"],
        "transfer_note": "Experience with text querying and NoSQL indexing aids in understanding Elasticsearch inverted indices."
    },

    # --- Cloud & DevOps ---
    "Git": {
        "category": "Cloud & DevOps",
        "aliases": ["git", "github", "gitlab", "version control", "bitbucket"],
        "foundations": ["Software Engineering", "Linux"],
        "transfer_note": "Standard development teamwork naturally builds familiarity with branching and commit workflows."
    },
    "Docker": {
        "category": "Cloud & DevOps",
        "aliases": ["docker", "containerization", "containers", "dockerfile", "docker-compose"],
        "foundations": ["Linux", "Git", "DevOps", "Backend Development"],
        "transfer_note": "Understanding environment dependencies and Linux process isolation creates an immediate bridge to Docker."
    },
    "Kubernetes": {
        "category": "Cloud & DevOps",
        "aliases": ["kubernetes", "k8s"],
        "foundations": ["Docker", "Linux", "Cloud Computing", "DevOps"],
        "transfer_note": "Proficiency in containerizing apps with Docker provides the prerequisite baseline for Kubernetes orchestration."
    },
    "AWS": {
        "category": "Cloud & DevOps",
        "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "foundations": ["Cloud Computing", "Linux", "Docker", "GCP", "Azure"],
        "transfer_note": "General cloud infrastructure and virtualization experience transfer readily across AWS services."
    },
    "Azure": {
        "category": "Cloud & DevOps",
        "aliases": ["azure", "microsoft azure"],
        "foundations": ["Cloud Computing", "AWS", "GCP", "C#"],
        "transfer_note": "Prior cloud or enterprise computing background easily maps to Azure resource groups and App Services."
    },
    "GCP": {
        "category": "Cloud & DevOps",
        "aliases": ["gcp", "google cloud", "google cloud platform"],
        "foundations": ["Cloud Computing", "AWS", "Docker", "Kubernetes"],
        "transfer_note": "Cloud native concepts like compute instances and managed Kubernetes map directly into Google Cloud."
    },
    "CI/CD": {
        "category": "Cloud & DevOps",
        "aliases": ["ci/cd", "ci cd", "continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"],
        "foundations": ["Git", "Docker", "Unit Testing", "DevOps"],
        "transfer_note": "Automated testing practices and script execution form the foundation of CI/CD build pipelines."
    },
    "Linux": {
        "category": "Cloud & DevOps",
        "aliases": ["linux", "unix", "bash", "shell scripting", "terminal"],
        "foundations": ["Git", "Docker", "Backend Development"],
        "transfer_note": "Using command line interfaces and developer tools establishes quick fluency with Linux shell commands."
    },

    # --- AI, ML & Data Science ---
    "Machine Learning": {
        "category": "AI & Data Science",
        "aliases": ["machine learning", "ml", "statistical modeling"],
        "foundations": ["Python", "Pandas", "NumPy", "Statistics", "Algorithms"],
        "transfer_note": "Python data handling and algorithmic problem solving prepare the ground for machine learning pipelines."
    },
    "Deep Learning": {
        "category": "AI & Data Science",
        "aliases": ["deep learning", "dl", "neural networks", "neural net"],
        "foundations": ["Machine Learning", "Python", "PyTorch", "TensorFlow"],
        "transfer_note": "Established familiarity with ML model training and matrix mathematics maps directly to neural architectures."
    },
    "PyTorch": {
        "category": "AI & Data Science",
        "aliases": ["pytorch", "torch"],
        "foundations": ["Python", "Machine Learning", "NumPy", "Deep Learning"],
        "transfer_note": "Python OOP and tensor manipulation with NumPy translate cleanly to PyTorch tensor operations."
    },
    "TensorFlow": {
        "category": "AI & Data Science",
        "aliases": ["tensorflow", "tf", "keras"],
        "foundations": ["Python", "Machine Learning", "Deep Learning"],
        "transfer_note": "Core machine learning workflows provide the intuition needed for TensorFlow graph execution."
    },
    "Pandas": {
        "category": "AI & Data Science",
        "aliases": ["pandas", "dataframe"],
        "foundations": ["Python", "SQL", "Data Analysis"],
        "transfer_note": "Tabular querying experience in SQL mirrors the data manipulation capabilities of Pandas DataFrames."
    },
    "NumPy": {
        "category": "AI & Data Science",
        "aliases": ["numpy", "numerical python"],
        "foundations": ["Python", "Pandas", "Mathematics"],
        "transfer_note": "Python array handling and linear algebra basics align seamlessly with NumPy vectorization."
    },
    "Natural Language Processing": {
        "category": "AI & Data Science",
        "aliases": ["nlp", "natural language processing", "text processing"],
        "foundations": ["Python", "Machine Learning", "Regex"],
        "transfer_note": "String parsing and feature engineering in Python provide the initial springboard into NLP tokenization."
    },

    # --- Software Architecture & Testing ---
    "Unit Testing": {
        "category": "Architecture & Testing",
        "aliases": ["unit testing", "unit tests", "pytest", "jest", "junit", "tdd", "test driven development"],
        "foundations": ["Python", "JavaScript", "Java", "Software Engineering"],
        "transfer_note": "Writing modular, testable application code makes test assertion suites intuitive to adopt."
    },
    "System Design": {
        "category": "Architecture & Testing",
        "aliases": ["system design", "software architecture", "scalability", "high availability", "distributed architecture"],
        "foundations": ["Backend & APIs", "Databases & Storage", "Microservices"],
        "transfer_note": "Hands-on experience with backend services and caching informs end-to-end scalable architecture design."
    },
    "Agile/Scrum": {
        "category": "Core & Professional",
        "aliases": ["agile", "scrum", "kanban", "sprint planning", "jira"],
        "foundations": ["Project Management", "Team Collaboration"],
        "transfer_note": "Structured project workflows and cross-functional team delivery align with Agile sprint cadences."
    },
    "Problem Solving": {
        "category": "Core & Professional",
        "aliases": ["problem solving", "analytical skills", "critical thinking", "data structures", "algorithms"],
        "foundations": ["Software Engineering"],
        "transfer_note": "Demonstrated technical project execution underscores strong analytical and troubleshooting discipline."
    },
    "Communication": {
        "category": "Core & Professional",
        "aliases": ["communication", "communication skills", "verbal communication", "written communication", "team collaboration", "interpersonal skills"],
        "foundations": ["Agile/Scrum", "Mentorship", "Documentation"],
        "transfer_note": "Collaborative project contributions and documentation authoring reflect core communication ability."
    }
}

# Pre-compile regex matchers for each skill
COMPILED_PATTERNS: Dict[str, List[re.Pattern]] = {}
for canonical_name, data in SKILL_TAXONOMY.items():
    patterns = []
    for alias in data["aliases"]:
        escaped = re.escape(alias.lower())
        # If alias ends or starts with special chars (like c++, c#), adjust boundary
        pattern_str = rf"(?<![a-zA-Z0-9_#+]){escaped}(?![a-zA-Z0-9_#+])"
        patterns.append(re.compile(pattern_str, re.IGNORECASE))
    COMPILED_PATTERNS[canonical_name] = patterns

# Requirement priority keywords
HIGH_PRIORITY_TERMS = [
    "must have", "required", "requirement", "essential", "mandatory",
    "minimum of", "proficiency in", "expert in", "demonstrated experience in",
    "core competency", "5+ years", "3+ years", "key requirement"
]
LOW_PRIORITY_TERMS = [
    "nice to have", "plus", "bonus", "preferred", "familiarity with",
    "exposure to", "optional", "good to have", "advantageous"
]

# Alternative career profiles catalog
CAREER_ROLES_CATALOG = [
    {
        "title": "Backend API Engineer",
        "key_skills": ["Python", "FastAPI", "Django", "SQL", "PostgreSQL", "REST APIs", "Docker", "Git", "Redis"],
        "description": "Designs, implements, and maintains robust server-side APIs, database schemas, and microservice communication."
    },
    {
        "title": "Full Stack Developer",
        "key_skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Python", "Node.js", "SQL", "Git", "REST APIs"],
        "description": "Bridges user-facing client interfaces with performant backend services and database storage."
    },
    {
        "title": "Frontend UI/UX Engineer",
        "key_skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Tailwind CSS", "Vue.js", "Next.js", "Git"],
        "description": "Crafts accessible, high-performance web applications and design system components for responsive user experiences."
    },
    {
        "title": "DevOps & Cloud Engineer",
        "key_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git", "Python", "Azure", "GCP"],
        "description": "Automates deployment pipelines, provisions resilient cloud infrastructure, and manages containerized orchestration."
    },
    {
        "title": "Data & ML Engineer",
        "key_skills": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "PostgreSQL", "Deep Learning", "PyTorch"],
        "description": "Constructs predictive intelligence models, clean data pipelines, and analytical processing engines."
    },
    {
        "title": "Software Systems & QA Engineer",
        "key_skills": ["Unit Testing", "Python", "Java", "Git", "Problem Solving", "CI/CD", "REST APIs", "Agile/Scrum"],
        "description": "Ensures software stability through rigorous test automation, continuous integration, and architectural verification."
    }
]


# ============================================================================
# EXTRACTION & CONTEXT HELPERS
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize raw text for consistent matching."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\t\r\f\v]+", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences while respecting common technical abbreviations."""
    if not text:
        return []
    # Replace newlines with periods if sentence looks fragmented
    cleaned = re.sub(r"\n+", ". ", text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def detect_skill_in_text(text: str, canonical_skill: str) -> bool:
    """Check if any compiled alias pattern for a canonical skill matches the text."""
    patterns = COMPILED_PATTERNS.get(canonical_skill, [])
    for pattern in patterns:
        if pattern.search(text):
            return True
    return False


def find_evidence_snippet(text: str, canonical_skill: str, max_chars: int = 180) -> Optional[str]:
    """Extract an exact sentence or clause from text serving as verified evidence for a skill."""
    sentences = split_into_sentences(text)
    for sentence in sentences:
        if detect_skill_in_text(sentence, canonical_skill):
            # Trim clean snippet
            snippet = sentence.strip()
            if len(snippet) > max_chars:
                snippet = snippet[:max_chars - 3].rstrip() + "..."
            return snippet

    # Fallback to line scanning
    for line in text.splitlines():
        if detect_skill_in_text(line, canonical_skill):
            clean_line = line.strip()
            if len(clean_line) > max_chars:
                clean_line = clean_line[:max_chars - 3].rstrip() + "..."
            return clean_line
    return None


def extract_skills_with_evidence(text: str) -> Dict[str, Dict[str, Any]]:
    """Scan text and return dictionary of detected canonical skills with their evidence snippets."""
    detected: Dict[str, Dict[str, Any]] = {}
    normalized = normalize_text(text)

    for skill, patterns in COMPILED_PATTERNS.items():
        found = False
        for pattern in patterns:
            if pattern.search(normalized):
                found = True
                break
        if found:
            evidence = find_evidence_snippet(text, skill)
            meta = SKILL_TAXONOMY[skill]
            detected[skill] = {
                "skill": skill,
                "category": meta["category"],
                "evidence": evidence or f"Identified in context as {skill}."
            }

    return detected


def assess_jd_priority(job_description: str, canonical_skill: str) -> Tuple[str, str]:
    """Determine requirement priority (High, Medium, Low) and rationale from the job description."""
    jd_lower = job_description.lower()
    patterns = COMPILED_PATTERNS.get(canonical_skill, [])

    # Find sentences mentioning this skill in the JD
    sentences = split_into_sentences(job_description)
    matching_sentences = [s for s in sentences if detect_skill_in_text(s, canonical_skill)]
    combined_context = " ".join(matching_sentences).lower()

    # Check for High priority indicators
    for term in HIGH_PRIORITY_TERMS:
        if term in combined_context:
            return ("High", f"Explicitly listed as essential: '{term}' in job specification.")

    # Check for Low priority / bonus indicators
    for term in LOW_PRIORITY_TERMS:
        if term in combined_context:
            return ("Low", f"Identified as preferred or bonus qualification ('{term}').")

    # Check mention frequency
    total_mentions = 0
    for pattern in patterns:
        total_mentions += len(pattern.findall(jd_lower))

    if total_mentions >= 3:
        return ("High", f"Emphasized multiple times ({total_mentions}x) throughout the job description.")
    elif total_mentions >= 1:
        return ("Medium", "Listed as a standard technical competency for this position.")

    return ("Medium", "Standard role requirement.")


# ============================================================================
# ROADMAP GENERATOR
# ============================================================================

def generate_7day_roadmap(missing_skills: List[Dict[str, Any]], resume_skills: List[str]) -> List[Dict[str, Any]]:
    """Generate a high-impact, 7-day personalized sprint targeting the candidate's top missing skills."""
    if not missing_skills:
        return [
            {
                "day": 1,
                "skill": "Advanced Optimization",
                "topic": "Architecture Refactoring",
                "task": "Review existing projects for modularity, clean code, and design patterns."
            },
            {
                "day": 2,
                "skill": "Testing & Coverage",
                "topic": "Automated Test Suites",
                "task": "Implement unit and integration tests reaching 85%+ branch coverage."
            },
            {
                "day": 3,
                "skill": "CI/CD Deployment",
                "topic": "Continuous Delivery Pipeline",
                "task": "Set up automated linting and deployment actions using GitHub Actions."
            },
            {
                "day": 4,
                "skill": "System Observability",
                "topic": "Telemetry & Logging",
                "task": "Add structured logging, request tracing, and error monitoring."
            },
            {
                "day": 5,
                "skill": "Database Tuning",
                "topic": "Index & Query Optimization",
                "task": "Profile execution plans (EXPLAIN ANALYZE) and optimize join bottlenecks."
            },
            {
                "day": 6,
                "skill": "Technical Documentation",
                "topic": "Architecture Decision Records (ADRs)",
                "task": "Document API contracts with OpenAPI specs and system topology diagrams."
            },
            {
                "day": 7,
                "skill": "Interview Demonstration",
                "topic": "Portfolio Showcase & Code Walkthrough",
                "task": "Record a concise 3-minute technical walkthrough demonstrating production readiness."
            }
        ]

    # Select up to top 3 missing skills
    targets = missing_skills[:3]
    roadmap: List[Dict[str, Any]] = []

    # Map out day allocation across targets
    if len(targets) == 1:
        s1 = targets[0]["skill"]
        roadmap = [
            {"day": 1, "skill": s1, "topic": f"{s1} Core Architecture & Syntax", "task": f"Setup official developer environment and implement fundamentals of {s1}."},
            {"day": 2, "skill": s1, "topic": f"{s1} State, Data & Error Handling", "task": f"Build practical modules handling data flow and edge case validation with {s1}."},
            {"day": 3, "skill": s1, "topic": f"{s1} Asynchronous & API Integration", "task": f"Connect {s1} with external endpoints or storage layers using modern patterns."},
            {"day": 4, "skill": s1, "topic": f"{s1} Performance & Optimization", "task": f"Profile and optimize memory, rendering, or query latency for {s1}."},
            {"day": 5, "skill": s1, "topic": f"{s1} Unit & Integration Testing", "task": f"Author comprehensive automated tests covering primary happy and error paths in {s1}."},
            {"day": 6, "skill": s1, "topic": f"{s1} Mini-Capstone Project Build", "task": f"Construct an end-to-end micro-project utilizing {s1} matching job requirements."},
            {"day": 7, "skill": s1, "topic": f"{s1} Deployment & Resume Story", "task": f"Deploy your {s1} repository and draft 3 quantifiable resume achievement bullet points."}
        ]
    elif len(targets) == 2:
        s1, s2 = targets[0]["skill"], targets[1]["skill"]
        roadmap = [
            {"day": 1, "skill": s1, "topic": f"{s1} Foundations & Setup", "task": f"Master basic primitives, conventions, and environment configuration for {s1}."},
            {"day": 2, "skill": s1, "topic": f"{s1} Core Production Patterns", "task": f"Build reusable components or services using idiomatic {s1} architecture."},
            {"day": 3, "skill": s1, "topic": f"{s1} Testing & Resilience", "task": f"Write integration tests and handle failover scenarios in {s1}."},
            {"day": 4, "skill": s2, "topic": f"{s2} Foundations & Tooling", "task": f"Explore {s2} syntax, core documentation, and setup a local proof-of-concept."},
            {"day": 5, "skill": s2, "topic": f"{s2} Applied Implementation", "task": f"Implement a functional feature integrating {s2} with real-world data structures."},
            {"day": 6, "skill": f"{s1} & {s2}", "topic": "Cross-Skill Integration", "task": f"Connect {s1} and {s2} in a unified project demonstrating interoperability."},
            {"day": 7, "skill": "Career Readiness", "topic": "Portfolio Artifact & Technical Narrative", "task": "Publish clean GitHub code repository with documentation and prepare interview talking points."}
        ]
    else:
        s1, s2, s3 = targets[0]["skill"], targets[1]["skill"], targets[2]["skill"]
        roadmap = [
            {"day": 1, "skill": s1, "topic": f"{s1} Core Architecture", "task": f"Establish environment and implement foundational concepts of {s1}."},
            {"day": 2, "skill": s1, "topic": f"{s1} Practical Implementation", "task": f"Develop a realistic module using {s1} demonstrating error handling and structure."},
            {"day": 3, "skill": s2, "topic": f"{s2} Quickstart & Core Idioms", "task": f"Learn foundational patterns, configuration, and syntax of {s2}."},
            {"day": 4, "skill": s2, "topic": f"{s2} Applied Exercises", "task": f"Build a practical exercise linking {s2} to backend services or client state."},
            {"day": 5, "skill": s3, "topic": f"{s3} Essentials & Industry Standards", "task": f"Understand core workflows, commands, and architecture for {s3}."},
            {"day": 6, "skill": f"{s1} & {s3}", "topic": "End-to-End Pipeline Integration", "task": f"Combine {s1} and {s3} in an integrated service workflow with unit test validation."},
            {"day": 7, "skill": "Career Showcase", "topic": "Capstone Deliverable & Interview Narrative", "task": "Document project metrics on GitHub and craft STAR interview stories for each new skill."}
        ]

    return roadmap


# ============================================================================
# CAREER RECOMMENDATIONS GENERATOR
# ============================================================================

def generate_career_recommendations(resume_skills: List[str]) -> List[Dict[str, Any]]:
    """Suggest high-compatibility alternative job roles based on actual detected resume skills."""
    recommendations = []
    resume_set = set(resume_skills)

    for role in CAREER_ROLES_CATALOG:
        required = role["key_skills"]
        overlapping = [s for s in required if s in resume_set]
        overlap_count = len(overlapping)
        total_key = len(required)

        # Calculate compatibility percentage
        compat_score = round((overlap_count / total_key) * 100) if total_key else 0

        # Build explainable rationale
        if overlap_count >= 3:
            rationale = (
                f"Your verified mastery in {', '.join(overlapping[:3])} provides a direct match "
                f"for the core technical responsibilities of this role."
            )
        elif overlap_count >= 1:
            rationale = (
                f"Your experience with {overlapping[0]} satisfies an essential pillar, "
                f"with manageable transition overhead."
            )
        else:
            rationale = (
                "Your foundational programming skill set provides an adaptable launchpad "
                "with focused upskilling in domain tooling."
            )

        recommendations.append({
            "title": role["title"],
            "match_score": max(compat_score, 45),  # Realistic minimum baseline for related tech roles
            "overlapping_skills": overlapping,
            "relevance_reason": rationale,
            "description": role["description"]
        })

    # Sort descending by match score
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:3]


# ============================================================================
# DYNAMIC AI EXECUTIVE SUMMARY
# ============================================================================

def generate_ai_summary(
    match_percentage: float,
    matched_skills: List[str],
    missing_skills: List[Dict[str, Any]],
    partial_skills: List[Dict[str, Any]]
) -> str:
    """Generate a crisp, professional, human-like executive summary of candidate alignment."""
    matched_count = len(matched_skills)
    missing_count = len(missing_skills)
    partial_count = len(partial_skills)

    top_matched = ", ".join(matched_skills[:4]) if matched_skills else "general foundational skills"
    top_missing = ", ".join([m["skill"] for m in missing_skills[:3]]) if missing_skills else "none"

    if match_percentage >= 80:
        tone = (
            f"Candidate displays exceptionally high technical alignment ({match_percentage}%) with this position. "
            f"Core strengths in {top_matched} satisfy the primary job requirements. "
        )
        if missing_count > 0:
            tone += f"Final Polish in {top_missing} will solidify complete role mastery."
        else:
            tone += "Candidate fully covers all key technical competencies outlined in the job description."
    elif match_percentage >= 60:
        tone = (
            f"Candidate presents a solid technical foundation ({match_percentage}% compatibility), "
            f"demonstrating verified competencies in {top_matched}. "
        )
        if partial_count > 0:
            tone += f"Detected {partial_count} partially supported competencies where underlying experience enables fast onboarding. "
        tone += f"Strategic upskilling in high-priority gaps ({top_missing}) will significantly elevate interview readiness."
    else:
        tone = (
            f"Candidate demonstrates foundational software engineering capability with key competencies in {top_matched}. "
            f"However, several essential role requirements ({top_missing}) are not explicitly represented in the resume. "
            f"Completing the targeted 7-day action sprint will bridge the primary gap areas and boost candidate competitiveness."
        )

    return tone


# ============================================================================
# MAIN MATCHING ENGINE
# ============================================================================

def match_skills(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Execute complete explainable resume and job description skill analysis."""
    # 1. Extract skills with verified evidence snippets
    resume_extracted = extract_skills_with_evidence(resume_text)
    jd_extracted = extract_skills_with_evidence(job_description)

    resume_skills = list(resume_extracted.keys())
    required_skills = list(jd_extracted.keys())

    # Fallback if no specific skills were detected in JD
    if not required_skills:
        # Default reasonable fallback so user gets actionable guidance
        default_skills = ["Python", "JavaScript", "SQL", "Git", "REST APIs", "Problem Solving"]
        for s in default_skills:
            if s not in jd_extracted:
                jd_extracted[s] = {
                    "skill": s,
                    "category": SKILL_TAXONOMY[s]["category"],
                    "evidence": "Extracted as standard core technical baseline."
                }
        required_skills = list(jd_extracted.keys())

    resume_skills_set = set(resume_skills)

    # 2. Classify into Matched, Partially Supported, and Missing
    matched_skills: List[str] = []
    matched_skill_details: List[Dict[str, Any]] = []

    partial_skills: List[str] = []
    partial_skill_details: List[Dict[str, Any]] = []

    missing_skills: List[str] = []
    missing_skill_details: List[Dict[str, Any]] = []

    # Prepare job description raw lines for citation
    jd_lines = [l.strip() for l in job_description.splitlines() if l.strip()]

    # Skill categories distribution tracking
    distribution: Dict[str, Dict[str, int]] = {
        "Frontend Development": {"resume": 0, "required": 0},
        "Backend & APIs": {"resume": 0, "required": 0},
        "Databases & Storage": {"resume": 0, "required": 0},
        "Cloud & DevOps": {"resume": 0, "required": 0},
        "AI & Data Science": {"resume": 0, "required": 0},
        "Architecture & Testing": {"resume": 0, "required": 0},
        "Core & Professional": {"resume": 0, "required": 0}
    }

    # Count categories for resume skills
    for s in resume_skills:
        cat = SKILL_TAXONOMY[s]["category"]
        if cat in distribution:
            distribution[cat]["resume"] += 1

    # Evaluate each required skill
    total_weighted_points = 0.0
    earned_weighted_points = 0.0

    for skill in required_skills:
        meta = SKILL_TAXONOMY[skill]
        cat = meta["category"]
        if cat in distribution:
            distribution[cat]["required"] += 1

        priority, priority_reason = assess_jd_priority(job_description, skill)
        weight = 1.3 if priority == "High" else (1.0 if priority == "Medium" else 0.7)
        total_weighted_points += weight

        # Matching line in job description
        matching_jd_lines = [
            l for l in jd_lines
            if detect_skill_in_text(l, skill)
        ]
        if not matching_jd_lines:
            matching_jd_lines = [jd_extracted[skill]["evidence"]]

        if skill in resume_skills_set:
            # DIRECT MATCH
            matched_skills.append(skill)
            earned_weighted_points += weight * 1.0
            matched_skill_details.append({
                "skill": skill,
                "category": cat,
                "priority": priority,
                "evidence": resume_extracted[skill]["evidence"],
                "job_description_lines": matching_jd_lines[:3]
            })
        else:
            # CHECK FOR PARTIAL FOUNDATION MATCH
            foundations = meta.get("foundations", [])
            overlapping_foundations = [f for f in foundations if f in resume_skills_set]

            if overlapping_foundations:
                # PARTIAL MATCH
                partial_skills.append(skill)
                earned_weighted_points += weight * 0.5  # Partial credit
                foundation_str = ", ".join(overlapping_foundations)
                partial_skill_details.append({
                    "skill": skill,
                    "category": cat,
                    "priority": priority,
                    "foundation_skill": foundation_str,
                    "explanation": (
                        f"While {skill} is not explicitly stated in your resume, you possess direct foundational "
                        f"experience in {foundation_str}. {meta.get('transfer_note', '')}"
                    ),
                    "job_description_lines": matching_jd_lines[:3]
                })
            else:
                # FULL MISSING
                missing_skills.append(skill)
                missing_skill_details.append({
                    "skill": skill,
                    "category": cat,
                    "priority": priority,
                    "priority_reason": priority_reason,
                    "reason": f"Required by the job description ({priority} priority) but no direct or foundational evidence was identified in the resume text.",
                    "job_description_lines": matching_jd_lines[:3]
                })

    # Sort missing skills by priority (High -> Medium -> Low)
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    missing_skill_details.sort(key=lambda x: priority_order.get(x["priority"], 2))

    # Match percentage calculation
    if total_weighted_points > 0:
        match_percentage = round((earned_weighted_points / total_weighted_points) * 100, 1)
    else:
        match_percentage = 0.0

    # Extract Top 3 missing skill priorities
    skill_priorities = []
    for item in missing_skill_details[:3]:
        skill_priorities.append({
            "skill": item["skill"],
            "priority": item["priority"],
            "reason": item["priority_reason"],
            "impact": (
                "Adding this skill addresses a core requirement and will noticeably improve candidate ranking."
                if item["priority"] == "High"
                else "Strengthens overall role qualification and eliminates a secondary gap."
            )
        })

    # Generate 7-day personalized roadmap
    learning_plan = generate_7day_roadmap(missing_skill_details, resume_skills)

    # Generate career recommendations
    career_recommendations = generate_career_recommendations(resume_skills)

    # Generate AI Executive Summary
    ai_summary = generate_ai_summary(match_percentage, matched_skills, missing_skill_details, partial_skill_details)

    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "partial_skills": partial_skills,
        "partially_matched_skills": partial_skills,
        "matched_skill_details": matched_skill_details,
        "missing_skill_details": missing_skill_details,
        "partial_skill_details": partial_skill_details,
        "match_percentage": match_percentage,
        "skill_priorities": skill_priorities,
        "skill_distribution": distribution,
        "ai_summary": ai_summary,
        "career_recommendations": career_recommendations,
        "learning_plan": learning_plan
    }
