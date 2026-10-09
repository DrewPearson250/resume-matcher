# Resume ↔ Internship Matcher

A Streamlit app that compares your resume against internship descriptions, scores each
one, shows the skills you're missing, and ranks them in a dashboard.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To try it right away, upload `samples/sample_resume.pdf` and click **Load 5 sample
internships** in the *Add / manage jobs* tab.

## How it works

| Step | File | What happens |
|---|---|---|
| Read PDF | `resume_parser.py` | Text is extracted with **PyMuPDF**, with **PyPDF2** as a fallback. |
| Extract info | `resume_parser.py`, `skills.py` | The text is split into sections (Education, Experience, …). Skills are found with a taxonomy of ~90 skills and their aliases. Regexes pull out the degree, major, school, GPA, graduation year and experience entries. Implied skills are added too (PyTorch → Python, Machine Learning). |
| Add jobs | `app.py`, `database.py` | Pasted descriptions are saved to **SQLite** (`resume_matcher.db`). The last resume is saved there as well, so it survives a page reload. |
| Match | `matcher.py` | Each job's skills are sorted into **required** or **preferred**, based on headers like "Preferred:" and "Nice to have". Skills joined by "or" ("Java or C++") count as one requirement that either skill satisfies. |
| Rank | `matcher.py`, `app.py` | Results go into a **pandas** DataFrame, sorted by score and shown in the dashboard. |

### Scoring

```
skill coverage  = (matched required + 0.5 × matched preferred) / (required + 0.5 × preferred)
text similarity = TF-IDF cosine similarity (scikit-learn, 1–2-grams), scaled ×2 and capped at 1
match score     = 70% skill coverage + 30% text similarity
```

If no known skills are found in a posting, the score falls back to text similarity alone.
The weights are constants at the top of `matcher.py`.

### Dashboard

- Summary metrics, plus a ranked table with match score, fit label, skill coverage and missing required skills
- Bar chart of match scores
- **Skills to learn next**: the missing skills that appear most often across your saved jobs
- Per-job breakdown: matched, missing required, and missing preferred skills, plus other
  high-weight keywords from the posting that aren't on your resume
- CSV export

The *Resume details* tab lets you add or remove skills to correct the extraction, and the
scores update right away.

## Limitations

- Skill detection is keyword-based. A skill that isn't in `skills.py` is only picked up
  through the TF-IDF text similarity. Add aliases to `SKILL_ALIASES` to extend it.
- Scanned (image-only) PDFs have no text layer, so they can't be read.
- The education and experience parsers rely on common resume layouts. Unusual layouts may
  only be partly extracted.
