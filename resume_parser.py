"""PDF text extraction and resume information extraction."""

import io
import re

from skills import CASE_SENSITIVE_PATTERNS, IMPLIED_SKILLS, SKILL_ALIASES

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None

try:
    from PyPDF2 import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None


# ---------------------------------------------------------------------------
# PDF reading
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF. Uses PyMuPDF, falling back to PyPDF2."""
    text = ""
    if fitz is not None:
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                text = "\n".join(page.get_text() for page in doc)
        except Exception:
            text = ""
    if not text.strip() and PdfReader is not None:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text


# ---------------------------------------------------------------------------
# Skill extraction
# ---------------------------------------------------------------------------

def _compile_skill_patterns():
    patterns = {}
    for skill, aliases in SKILL_ALIASES.items():
        if skill in CASE_SENSITIVE_PATTERNS:
            patterns[skill] = re.compile(CASE_SENSITIVE_PATTERNS[skill])
        else:
            alt = "|".join(aliases)
            # Custom boundaries so "c++", "c#", "node.js" etc. still match.
            patterns[skill] = re.compile(rf"(?<![\w]){'(?:' + alt + ')'}(?![\w])", re.IGNORECASE)
    return patterns


_SKILL_PATTERNS = _compile_skill_patterns()


def find_skill_mentions(text: str) -> list:
    """Return (start, end, skill) for the first mention of each skill, sorted by position."""
    mentions = []
    for skill, pat in _SKILL_PATTERNS.items():
        m = pat.search(text)
        if m:
            mentions.append((m.start(), m.end(), skill))
    return sorted(mentions)


def extract_skills(text: str) -> set:
    """Return the set of canonical skill names found in the text."""
    return {skill for skill, pat in _SKILL_PATTERNS.items() if pat.search(text)}


def expand_implied(skills) -> set:
    """Add broader skills implied by specific ones (PyTorch -> Machine Learning, ...)."""
    result = set(skills)
    frontier = list(result)
    while frontier:
        for implied in IMPLIED_SKILLS.get(frontier.pop(), []):
            if implied not in result:
                result.add(implied)
                frontier.append(implied)
    return result


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

SECTION_HEADERS = {
    "education": ["education", "academic background", "academics"],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment", "internships", "internship experience", "relevant experience",
    ],
    "projects": ["projects", "personal projects", "academic projects"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "other": [
        "certifications", "awards", "honors", "activities", "leadership",
        "volunteer", "publications", "interests", "summary", "objective",
    ],
}

_HEADER_LOOKUP = {h: sec for sec, hs in SECTION_HEADERS.items() for h in hs}


def split_sections(text: str) -> dict:
    """Split resume text into sections based on common header lines."""
    sections = {"header": []}
    current = "header"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if key in _HEADER_LOOKUP and len(line) < 40:
            current = _HEADER_LOOKUP[key]
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v) for k, v in sections.items() if v}


# ---------------------------------------------------------------------------
# Education & experience
# ---------------------------------------------------------------------------

DEGREE_RE = re.compile(
    r"\b(Bachelor(?:'s)?(?: of [A-Z][\w ]+)?|Master(?:'s)?(?: of [A-Z][\w ]+)?|"
    r"Ph\.?D\.?|Doctor(?:ate)?|Associate(?:'s)?(?: of [A-Z][\w ]+)?|"
    r"B\.?S\.?c?|B\.?A\.?|M\.?S\.?c?|M\.?A\.?|B\.?Eng|M\.?Eng|MBA)\b"
)
SCHOOL_RE = re.compile(
    r"([A-Z][\w.&'-]*(?:\s+(?:of|at|and|&|[A-Z][\w.&'-]*))*\s+"
    r"(?:University|College|Institute|School)(?:\s+of\s+[A-Z][\w-]*(?:\s+[A-Z][\w-]*)*)?|"
    r"(?:University|College|Institute)\s+of\s+[A-Z][\w-]*(?:\s+[A-Z][\w-]*)*)"
)
GPA_RE = re.compile(r"\bGPA[:\s]*([0-4]\.\d{1,2})(?:\s*/\s*4\.0+)?", re.IGNORECASE)
GRAD_RE = re.compile(
    r"\b(?:(?:Expected|Graduat\w*|Class of)[:\s]*)?"
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+)?(20\d{2})\b"
)
MAJOR_RE = re.compile(
    r"\b(?:in|of)\s+((?:Computer|Data|Electrical|Mechanical|Software|Information|Applied|Business|"
    r"Industrial|Chemical|Civil|Biomedical|Cognitive|Mathematics|Math|Statistics|Physics|Economics|"
    r"Finance|Accounting|Marketing|Biology|Chemistry)[\w ]{0,40})",
)

DATE_RANGE_RE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|"
    r"(?:Summer|Fall|Spring|Winter)\s+\d{4}|\d{1,2}/\d{4}|\d{4})\s*[-–—to]+\s*"
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|"
    r"(?:Summer|Fall|Spring|Winter)\s+\d{4}|\d{1,2}/\d{4}|\d{4}|Present|Current|Now)",
    re.IGNORECASE,
)
TITLE_WORDS = re.compile(
    r"\b(Intern|Internship|Engineer|Developer|Analyst|Assistant|Researcher|Associate|"
    r"Consultant|Manager|Scientist|Tutor|Teaching Assistant|Fellow|Coordinator|Lead|Specialist)\b",
    re.IGNORECASE,
)


def extract_education(text: str, sections: dict) -> dict:
    edu_text = sections.get("education") or text
    degree = DEGREE_RE.search(edu_text)
    school = SCHOOL_RE.search(edu_text)
    gpa = GPA_RE.search(edu_text)
    major = MAJOR_RE.search(edu_text)
    years = [int(m.group(2)) for m in GRAD_RE.finditer(edu_text)]
    return {
        "degree": degree.group(0).strip() if degree else None,
        "major": major.group(1).strip().rstrip(",") if major else None,
        "school": school.group(0).strip() if school else None,
        "gpa": float(gpa.group(1)) if gpa else None,
        "graduation_year": max(years) if years else None,
        "raw": edu_text if "education" in sections else None,
    }


def extract_experience(sections: dict) -> list:
    """Return a list of experience entries: {title, dates, details}."""
    exp_text = sections.get("experience", "")
    if not exp_text:
        return []
    entries, current = [], None
    for line in exp_text.splitlines():
        is_bullet = line[:1] in "•●▪-*–·◦"
        date = DATE_RANGE_RE.search(line)
        looks_like_heading = not is_bullet and (date or (TITLE_WORDS.search(line) and len(line) < 90))
        if looks_like_heading and (current is None or current["details"] or date and current["dates"]):
            current = {"title": DATE_RANGE_RE.sub("", line).strip(" |,–-"), "dates": None, "details": []}
            entries.append(current)
            if date:
                current["dates"] = date.group(0)
        elif current is None:
            current = {"title": line, "dates": None, "details": []}
            entries.append(current)
        elif not is_bullet and not current["details"] and not current["dates"] and date:
            current["dates"] = date.group(0)
            extra = DATE_RANGE_RE.sub("", line).strip(" |,–-")
            if extra:
                current["title"] = f"{current['title']} — {extra}"
        elif not is_bullet and not current["details"]:
            current["title"] = f"{current['title']} — {line}"
        else:
            current["details"].append(line.lstrip("•●▪-*–·◦ ").strip())
    return entries


def parse_resume(text: str) -> dict:
    sections = split_sections(text)
    return {
        "text": text,
        "sections": sections,
        "skills": sorted(expand_implied(extract_skills(text))),
        "education": extract_education(text, sections),
        "experience": extract_experience(sections),
    }
