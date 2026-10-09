"""Generate samples/sample_resume.pdf for trying out the app."""
import fitz

LINES = """Jordan Rivera
jordan.rivera@example.edu | (555) 123-4567 | github.com/jrivera

EDUCATION
Rutgers University, New Brunswick
Bachelor of Science in Computer Science, Minor in Statistics
Expected May 2027 | GPA: 3.7/4.0

EXPERIENCE
Data Analyst Intern, Acme Retail Co.
June 2025 - August 2025
• Built a demand forecasting model in Python with pandas and scikit-learn, improving accuracy by 12%
• Wrote SQL queries against a PostgreSQL warehouse and built Tableau dashboards for leadership
• Presented findings to stakeholders, strengthening communication across teams

Undergraduate Teaching Assistant, Rutgers Computer Science Department
Sep 2024 - Present
• Lead weekly recitations for Data Structures (Java) for 40 students
• Grade assignments and hold office hours focused on algorithms and problem solving

PROJECTS
Resume Matcher - Streamlit app that ranks internships using TF-IDF similarity (Python, scikit-learn, SQLite)
Sentiment Classifier - Fine-tuned a PyTorch NLP model on product reviews in Jupyter

SKILLS
Languages: Python, Java, SQL, JavaScript, HTML/CSS
Tools: Git, Linux, Docker, NumPy, Matplotlib, Excel
""".splitlines()

doc = fitz.open()
page = doc.new_page()
y = 50
for line in LINES:
    bold = line.isupper() or line == LINES[0]
    page.insert_text((50, y), line, fontsize=13 if line == LINES[0] else 10.5,
                     fontname="helv" if not bold else "hebo")
    y += 18 if bold else 15
doc.save("samples/sample_resume.pdf")
print("wrote samples/sample_resume.pdf")
