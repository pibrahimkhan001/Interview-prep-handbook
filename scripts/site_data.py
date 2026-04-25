"""
Shared site metadata: topics, parts, and slug generation.
Used by all generator scripts.
"""

# Organize topics into "Parts" similar to reference site
PARTS = [
    {
        "id": 1,
        "label": "Part 1",
        "title": "Core Programming Languages",
        "desc": "Build mastery of the languages that power modern web applications. JavaScript for everything client and server, Python for versatility.",
        "topics": ["JavaScript", "Python"],
    },
    {
        "id": 2,
        "label": "Part 2",
        "title": "Web Fundamentals",
        "desc": "Structure and style: the two pillars every web developer must know deeply.",
        "topics": ["HTML", "CSS"],
    },
    {
        "id": 3,
        "label": "Part 3",
        "title": "Backend Technologies",
        "desc": "Server-side runtimes, web frameworks, and API design — from listening on a port to building a production-ready REST service.",
        "topics": ["Node.Js", "ExpressJS", "API"],
    },
    {
        "id": 4,
        "label": "Part 4",
        "title": "Frontend Frameworks",
        "desc": "Modern component architecture, state management, and the React ecosystem.",
        "topics": ["ReactJS"],
    },
    {
        "id": 5,
        "label": "Part 5",
        "title": "Databases",
        "desc": "Relational and document stores — when to use which, how to design schemas, and how to query them efficiently.",
        "topics": ["MYSQL", "MongoDB"],
    },
    {
        "id": 6,
        "label": "Part 6",
        "title": "System Design & DevOps",
        "desc": "Architect MERN applications at scale, set up cloud infrastructure, and automate delivery with modern CI/CD pipelines.",
        "topics": ["System Design MERN Stack", "Infrastructure MERN Stack", "CI/CD Pipeline"],
    },
]

# Human-readable slugs for each topic + level combination
TOPIC_SLUGS = {
    "JavaScript": "javascript",
    "Python": "python",
    "HTML": "html",
    "CSS": "css",
    "Node.Js": "nodejs",
    "ExpressJS": "expressjs",
    "API": "api",
    "ReactJS": "reactjs",
    "MYSQL": "mysql",
    "MongoDB": "mongodb",
    "System Design MERN Stack": "system-design-mern",
    "Infrastructure MERN Stack": "infrastructure-mern",
    "CI/CD Pipeline": "cicd-pipeline",
}

LEVEL_SLUGS = {
    "Basic": "basic",
    "Tricky": "tricky",
    "Coding": "coding",
    "Advanced": "advanced",
    "Advanced Coding": "advanced-coding",
    "Scenario Based": "scenario",
    "Advanced Scenario Based": "advanced-scenario",
}

LEVEL_ORDER = ["Basic", "Tricky", "Coding", "Advanced", "Advanced Coding", "Scenario Based", "Advanced Scenario Based"]

LEVEL_DESCRIPTIONS = {
    "Basic":                    "Foundational knowledge — definitions, syntax, and core mechanics every beginner should know.",
    "Tricky":                   "Nuanced questions that separate strong candidates from ordinary ones. Edge cases, gotchas, and conceptual subtleties.",
    "Coding":                   "Practical coding problems with full solutions and line-by-line explanations.",
    "Advanced":                 "Deep internals, architecture decisions, and questions typical of senior-level interviews.",
    "Advanced Coding":          "Algorithmically challenging problems — data structures, performance optimization, and tricky logic.",
    "Scenario Based":           "Real-world situational questions — how you'd approach a concrete design or debugging problem.",
    "Advanced Scenario Based":  "Senior-level system design scenarios — trade-offs, scalability, and architectural reasoning.",
}

LEVEL_TIME_ESTIMATE = {
    "Basic": "60 min read",
    "Tricky": "75 min read",
    "Coding": "90 min read",
    "Advanced": "90 min read",
    "Advanced Coding": "100 min read",
    "Scenario Based": "75 min read",
    "Advanced Scenario Based": "90 min read",
}


def slug_for(topic, level):
    """Return file slug like `javascript-basic` for a (topic, level) pair."""
    t = TOPIC_SLUGS[topic]
    l = LEVEL_SLUGS[level]
    return f"{t}-{l}"


def file_for(topic, level):
    """Return chapter filename."""
    return f"{slug_for(topic, level)}.html"


def topic_part(topic):
    """Return the Part that a topic belongs to."""
    for p in PARTS:
        if topic in p["topics"]:
            return p
    return None
