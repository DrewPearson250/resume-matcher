"""Resume-to-job matching using skill overlap plus TF-IDF text similarity."""

import re

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_parser import expand_implied, find_skill_mentions
from skills import SKILL_ALIASES

# Final score = SKILL_WEIGHT * skill coverage + TEXT_WEIGHT * text similarity.
SKILL_WEIGHT = 0.7
TEXT_WEIGHT = 0.3
# Raw TF-IDF cosine between a resume and a job post rarely exceeds ~0.5 even for a
# strong match, so it is scaled up (and capped at 1) before blending.
TEXT_SIM_SCALE = 2.0
# Preferred / nice-to-have skills count half as much as required ones.
PREFERRED_WEIGHT = 0.5

PREFERRED_HEADER_RE = re.compile(r"preferred|nice[- ]to[- ]have|bonus|\ba plus\b|desired|optional", re.I)
REQUIRED_HEADER_RE = re.compile(r"required|requirements|qualifications|must[- ]have|minimum|basic", re.I)

# Words common in job posts that carry no signal about skills.
JOB_STOP_WORDS = list(ENGLISH_STOP_WORDS | {
    "experience", "work", "working", "team", "ability", "strong", "skills", "knowledge",
    "including", "intern", "internship", "role", "candidate", "candidates", "students",
    "student", "years", "year", "position", "opportunity", "company", "join", "looking",
    "preferred", "required", "requirements", "qualifications", "responsibilities", "plus",
    "related", "etc", "will", "help", "new", "using", "use", "understanding", "familiarity",
    "proficiency", "excellent", "good", "great", "summer", "currently", "pursuing", "degree",
    "field", "equivalent", "apply", "benefits", "pay", "hour", "hourly", "salary",
    "nice", "bonus", "points", "non", "solid", "exposure", "closely", "duties", "seeking",
    "hiring", "build", "builds", "day", "week", "weeks", "comfortable", "able", "prior",
    "proven", "eager", "passionate", "fast", "paced", "environment", "assist", "support",
})


OR_CONNECTOR_RE = re.compile(r"^\s*,?\s*(or|and/or|/)\s*$", re.I)


def _alternative_groups(line: str) -> list:
    """Group skills joined by "or" / "/" in a line, e.g. "Java or C++" -> {Java, C++}."""
    mentions = find_skill_mentions(line)
    groups = []
    for i, (start, end, skill) in enumerate(mentions):
        if i > 0 and OR_CONNECTOR_RE.match(line[mentions[i - 1][1]:start]):
            groups[-1].add(skill)
        else:
            groups.append({skill})
    return groups


def extract_requirements(job_text: str) -> list:
    """Return a list of (alternatives, kind) requirements found in a job description.

    `alternatives` is a frozenset of skills, any one of which satisfies the
    requirement. `kind` is "required" or "preferred": a line is preferred if it
    sits under a preferred-style header or itself says "preferred"/"a plus"/etc.
    """
    reqs = {}
    mode = "required"
    for line in job_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        is_header = len(stripped) < 60 and (stripped.endswith(":") or stripped.isupper() or not re.search(r"[.,;]", stripped))
        if is_header and PREFERRED_HEADER_RE.search(stripped):
            mode = "preferred"
        elif is_header and REQUIRED_HEADER_RE.search(stripped):
            mode = "required"
        kind = "preferred" if mode == "preferred" or PREFERRED_HEADER_RE.search(stripped) else "required"
        for group in _alternative_groups(stripped):
            key = frozenset(group)
            if reqs.get(key) != "required":  # required wins if mentioned both ways
                reqs[key] = kind

    # A skill required on its own makes any group containing it redundant.
    singles = {next(iter(g)) for g, k in reqs.items() if len(g) == 1}
    reqs = {g: k for g, k in reqs.items() if len(g) == 1 or not (g & singles)}
    # A skill listed alone in several places should count once (keep strongest kind).
    return sorted(reqs.items(), key=lambda gk: (gk[1], sorted(gk[0])))


def split_required_preferred(job_text: str):
    """Flattened (required_skills, preferred_skills) for display."""
    required, preferred = set(), set()
    for group, kind in extract_requirements(job_text):
        (required if kind == "required" else preferred).update(group)
    return required, preferred - required


def _fmt(group) -> str:
    return " or ".join(sorted(group, key=str.lower))


def text_similarities(resume_text: str, job_texts: list):
    """TF-IDF cosine similarity between the resume and each job description."""
    if not job_texts:
        return [], None, None
    vectorizer = TfidfVectorizer(stop_words=JOB_STOP_WORDS, ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    matrix = vectorizer.fit_transform([resume_text] + list(job_texts))
    return cosine_similarity(matrix[0:1], matrix[1:]).flatten().tolist(), vectorizer, matrix


def missing_keywords(vectorizer, matrix, job_index: int, resume_text: str, exclude: str = "", top_n: int = 8):
    """Highest-weighted single-word TF-IDF terms in a job that never appear in the resume.

    `exclude` is extra text (e.g. the company name / job title) whose words are skipped.
    """
    row = matrix[job_index + 1].toarray().flatten()
    terms = vectorizer.get_feature_names_out()
    resume_lower = resume_text.lower()
    exclude_words = set(re.findall(r"[a-z0-9]+", exclude.lower()))
    out = []
    for idx in row.argsort()[::-1]:
        if row[idx] <= 0 or len(out) >= top_n:
            break
        term = terms[idx]
        if " " in term or term.isdigit() or len(term) < 3 or term in resume_lower or term in exclude_words:
            continue
        out.append(term)
    return out


def score_job(resume_skills: set, job_text: str, text_sim: float) -> dict:
    reqs = extract_requirements(job_text)
    total_weight = matched_weight = 0.0
    matched, missing_req, missing_pref, job_skills = set(), [], [], set()
    for group, kind in reqs:
        weight = 1.0 if kind == "required" else PREFERRED_WEIGHT
        total_weight += weight
        job_skills |= group
        hit = group & resume_skills
        if hit:
            matched_weight += weight
            matched |= hit
        else:
            (missing_req if kind == "required" else missing_pref).append(_fmt(group))

    skill_cov = matched_weight / total_weight if total_weight else None  # None -> text only
    text_component = min(1.0, text_sim * TEXT_SIM_SCALE)
    if skill_cov is None:
        score = text_component
    else:
        score = SKILL_WEIGHT * skill_cov + TEXT_WEIGHT * text_component

    return {
        "score": round(100 * score, 1),
        "skill_coverage": None if skill_cov is None else round(100 * skill_cov, 1),
        "text_similarity": round(100 * text_sim, 1),
        "matched_skills": sorted(matched, key=str.lower),
        "missing_required": sorted(missing_req, key=str.lower),
        "missing_preferred": sorted(missing_pref, key=str.lower),
        "job_skills": sorted(job_skills, key=str.lower),
    }


def rank_jobs(resume: dict, jobs: pd.DataFrame) -> pd.DataFrame:
    """Score every job in `jobs` (needs a 'description' column) and sort by score."""
    if jobs.empty:
        return jobs.assign(score=[])
    resume_skills = expand_implied(resume["skills"])
    sims, vectorizer, matrix = text_similarities(resume["text"], jobs["description"].tolist())

    rows = []
    for i, (job, sim) in enumerate(zip(jobs.to_dict("records"), sims)):
        result = score_job(resume_skills, job["description"], sim)
        # Skip the company/title and skills already reported as matched or missing.
        skill_words = " ".join(" ".join([s] + SKILL_ALIASES.get(s, [])) for s in result["job_skills"])
        exclude = f"{job.get('title') or ''} {job.get('company') or ''} {skill_words}"
        result["missing_keywords"] = missing_keywords(vectorizer, matrix, i, resume["text"], exclude)
        rows.append(result)

    results = pd.concat([jobs.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    results = results.sort_values("score", ascending=False).reset_index(drop=True)
    results.insert(0, "rank", range(1, len(results) + 1))
    return results


def match_label(score: float) -> str:
    if score >= 75:
        return "Strong match"
    if score >= 55:
        return "Good match"
    if score >= 35:
        return "Partial match"
    return "Weak match"
