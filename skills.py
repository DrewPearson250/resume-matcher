"""Skill taxonomy used to detect skills in resumes and job descriptions.

Each canonical skill maps to a list of aliases (regex-safe, lowercase).
Extend this dictionary to support more domains.
"""

SKILL_ALIASES = {
    # Programming languages
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js", "es6"],
    "TypeScript": ["typescript", "ts"],
    "C": ["c"],
    "C++": ["c\\+\\+", "cpp"],
    "C#": ["c#", "c sharp"],
    "Go": ["golang", "go"],
    "Rust": ["rust"],
    "Ruby": ["ruby"],
    "PHP": ["php"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "R": ["r"],
    "MATLAB": ["matlab"],
    "Scala": ["scala"],
    "Bash": ["bash", "shell scripting", "shell"],
    "SQL": ["sql"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3", "sass", "scss"],

    # Web / frameworks
    "React": ["react", "react\\.js", "reactjs"],
    "Angular": ["angular"],
    "Vue": ["vue", "vue\\.js", "vuejs"],
    "Node.js": ["node", "node\\.js", "nodejs"],
    "Express": ["express", "express\\.js"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Spring": ["spring", "spring boot"],
    "Next.js": ["next\\.js", "nextjs"],
    "REST APIs": ["rest", "restful", "rest api", "rest apis"],
    "GraphQL": ["graphql"],

    # Data / ML
    "pandas": ["pandas"],
    "NumPy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch", "torch"],
    "Keras": ["keras"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "opencv"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Visualization": ["data visualization", "matplotlib", "seaborn", "plotly"],
    "Statistics": ["statistics", "statistical"],
    "Tableau": ["tableau"],
    "Power BI": ["power bi", "powerbi"],
    "Excel": ["excel", "microsoft excel"],
    "Spark": ["spark", "pyspark", "apache spark"],
    "Hadoop": ["hadoop"],
    "Jupyter": ["jupyter"],
    "Streamlit": ["streamlit"],

    # Databases
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "SQLite": ["sqlite"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "NoSQL": ["nosql"],

    # Cloud / DevOps
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "continuous integration", "github actions", "jenkins"],
    "Linux": ["linux", "unix"],
    "Git": ["git", "github", "gitlab"],
    "Terraform": ["terraform"],

    # Practices / concepts
    "Agile": ["agile", "scrum"],
    "Unit Testing": ["unit testing", "pytest", "junit", "jest", "testing"],
    "Object-Oriented Programming": ["object-oriented", "object oriented", "oop"],
    "Data Structures": ["data structures"],
    "Algorithms": ["algorithms"],
    "Microservices": ["microservices"],
    "Cybersecurity": ["cybersecurity", "security", "network security"],
    "Networking": ["networking", "tcp/ip"],
    "Embedded Systems": ["embedded systems", "embedded", "arduino", "raspberry pi"],
    "Mobile Development": ["android", "ios", "mobile development", "react native", "flutter"],
    "UI/UX": ["ui/ux", "figma", "user experience", "ux"],

    # Soft skills
    "Communication": ["communication", "communicate"],
    "Teamwork": ["teamwork", "collaboration", "collaborate", "team player"],
    "Leadership": ["leadership", "led", "lead"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Project Management": ["project management"],
}

# Skills whose names are short or double as everyday English words ("react", "excel",
# "Spring 2025", "the rest"). These replace the aliases above and are matched
# case-sensitively against the original text to avoid false positives.
CASE_SENSITIVE_PATTERNS = {
    "C": r"(?<![\w+#/])C(?![\w+#/])",
    "R": r"(?<![\w&/])R(?![\w&/])",
    "Go": r"\bGo(lang)?\b(?!\s+(to|back|through|over)\b)|\bgolang\b",
    "TypeScript": r"\bTypeScript\b|\bTS\b",
    "JavaScript": r"\bJavaScript\b|\bJS\b|\bES6\b",
    "Machine Learning": r"\b[Mm]achine [Ll]earning\b|\bML\b",
    "UI/UX": r"\bUI/UX\b|\bUX\b|\b[Ff]igma\b|\b[Uu]ser [Ee]xperience\b",
    "Leadership": r"\b[Ll]eadership\b",
    "React": r"\bReact(\.js|JS)?\b|\breactjs\b",
    "Excel": r"\b(Microsoft |MS )?Excel\b",
    "Spring": r"\bSpring (Boot|Framework|MVC)\b|\bJava Spring\b",
    "REST APIs": r"\bREST(ful)?\b|\b[Rr]estful\b",
    "Swift": r"\bSwift(UI)?\b",
    "Rust": r"\bRust\b",
    "Express": r"\bExpress(\.js)?\b",
    "Node.js": r"\bNode(\.js|JS)?\b|\bnode\.js\b|\bnodejs\b",
    "Spark": r"\b(Apache )?Spark\b|\bPySpark\b|\bpyspark\b",
}

# Having the key skill on a resume implies the listed broader skills
# (e.g. a PyTorch user knows Python and machine learning).
IMPLIED_SKILLS = {
    "pandas": ["Python", "Data Analysis"],
    "NumPy": ["Python"],
    "scikit-learn": ["Python", "Machine Learning"],
    "TensorFlow": ["Python", "Machine Learning", "Deep Learning"],
    "PyTorch": ["Python", "Machine Learning", "Deep Learning"],
    "Keras": ["Python", "Machine Learning", "Deep Learning"],
    "Deep Learning": ["Machine Learning"],
    "NLP": ["Machine Learning"],
    "Computer Vision": ["Machine Learning"],
    "Django": ["Python"],
    "Flask": ["Python"],
    "FastAPI": ["Python"],
    "Streamlit": ["Python"],
    "Spring": ["Java"],
    "React": ["JavaScript"],
    "Angular": ["TypeScript"],
    "Vue": ["JavaScript"],
    "Next.js": ["React", "JavaScript"],
    "Node.js": ["JavaScript"],
    "Express": ["Node.js", "JavaScript"],
    "TypeScript": ["JavaScript"],
    "MySQL": ["SQL"],
    "PostgreSQL": ["SQL"],
    "SQLite": ["SQL"],
    "Kubernetes": ["Docker"],
    "Tableau": ["Data Visualization"],
    "Power BI": ["Data Visualization"],
}
