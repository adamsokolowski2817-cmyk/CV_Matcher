import re


SKILLS = {
    "python": ["python", "py"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular"],
    "vue": ["vue", "vue.js"],
    "node.js": ["node", "node.js", "nodejs"],
    "html": ["html"],
    "css": ["css"],
    "sql": ["sql"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git", "github", "gitlab"],
    "linux": ["linux"],
    "rest api": ["rest api", "rest", "api"],
    "graphql": ["graphql"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring": ["spring", "spring boot"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration"],
    "jira": ["jira"],
    "excel": ["excel"],
    "power bi": ["power bi", "powerbi"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "machine learning": ["machine learning", "ml"],
    "data science": ["data science"],
    "scrum": ["scrum"],
    "agile": ["agile"],
    "english": ["angielski", "english", "b2", "c1"],
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("c++", "cpp")
    text = text.replace("c#", "csharp")
    text = re.sub(r"[^a-z0-9ąćęłńóśźż+#./ -]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text: str) -> set[str]:
    text = normalize_text(text)
    found = set()

    for skill, variants in SKILLS.items():
        for variant in variants:
            variant_norm = normalize_text(variant)
            pattern = r"(?<![a-z0-9])" + re.escape(variant_norm) + r"(?![a-z0-9])"

            if re.search(pattern, text):
                found.add(skill)
                break

    return found