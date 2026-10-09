"""Resume Matcher — rank internship postings by how well they fit your resume.

Run with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

import database as db
from matcher import match_label, rank_jobs, split_required_preferred
from resume_parser import extract_text_from_pdf, parse_resume
from sample_data import SAMPLE_JOBS
from skills import SKILL_ALIASES

st.set_page_config(page_title="Resume Matcher", page_icon="🎯", layout="wide")
db.init_db()


def badges(skills, color):
    if not skills:
        return "_none_"
    return " ".join(f":{color}-badge[{s}]" for s in skills)


# ---------------------------------------------------------------------------
# Resume state (persisted in SQLite so it survives page reloads)
# ---------------------------------------------------------------------------
if "resume" not in st.session_state:
    st.session_state.resume_name, st.session_state.resume = db.load_resume()

with st.sidebar:
    st.header("📄 Your resume")
    uploaded = st.file_uploader("Upload a PDF resume", type=["pdf"])
    if uploaded is not None and uploaded.name != st.session_state.get("last_upload"):
        with st.spinner("Reading resume…"):
            text = extract_text_from_pdf(uploaded.getvalue())
        if not text.strip():
            st.error("No text could be extracted. Scanned/image-only PDFs aren't supported.")
        else:
            parsed = parse_resume(text)
            db.save_resume(uploaded.name, parsed)
            st.session_state.resume = parsed
            st.session_state.resume_name = uploaded.name
            st.session_state.last_upload = uploaded.name
            st.success("Resume parsed!")

    if st.session_state.resume:
        st.caption(f"Loaded: **{st.session_state.resume_name}**")
        st.metric("Skills detected", len(st.session_state.resume["skills"]))
        if st.button("Remove resume"):
            db.clear_resume()
            st.session_state.resume = None
            st.session_state.resume_name = None
            st.rerun()
    else:
        st.info("Upload a resume to start matching.")

    st.divider()
    jobs_df = db.get_jobs()
    st.metric("Saved jobs", len(jobs_df))

st.title("🎯 Resume ↔ Internship Matcher")
tab_dash, tab_jobs, tab_resume = st.tabs(["🏆 Dashboard", "➕ Add / manage jobs", "📄 Resume details"])

resume = st.session_state.resume

# ---------------------------------------------------------------------------
# Resume details
# ---------------------------------------------------------------------------
with tab_resume:
    if not resume:
        st.info("Upload a PDF resume in the sidebar to see what was extracted.")
    else:
        st.subheader("Skills")
        st.caption("Detected automatically — add or remove skills to correct the extraction.")
        all_skills = sorted(set(SKILL_ALIASES) | set(resume["skills"]), key=str.lower)
        edited = st.multiselect("Your skills", all_skills, default=resume["skills"], label_visibility="collapsed")
        if sorted(edited) != sorted(resume["skills"]):
            resume["skills"] = sorted(edited)
            db.save_resume(st.session_state.resume_name, resume)
            st.rerun()

        col_edu, col_exp = st.columns([1, 2])
        with col_edu:
            st.subheader("Education")
            edu = resume["education"]
            fields = {
                "School": edu.get("school"),
                "Degree": edu.get("degree"),
                "Major": edu.get("major"),
                "GPA": edu.get("gpa"),
                "Graduation year": edu.get("graduation_year"),
            }
            for label, value in fields.items():
                st.markdown(f"**{label}:** {value if value is not None else '—'}")
            if edu.get("raw"):
                with st.expander("Education section text"):
                    st.text(edu["raw"])

        with col_exp:
            st.subheader("Experience")
            if not resume["experience"]:
                st.write("No experience section detected.")
            for entry in resume["experience"]:
                header = entry["title"] + (f"  ·  _{entry['dates']}_" if entry["dates"] else "")
                st.markdown(f"**{header}**")
                for d in entry["details"]:
                    st.markdown(f"- {d}")

        with st.expander("Raw extracted text"):
            st.text(resume["text"])

# ---------------------------------------------------------------------------
# Add / manage jobs
# ---------------------------------------------------------------------------
with tab_jobs:
    st.subheader("Add an internship")
    with st.form("add_job", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Job title *")
        company = c2.text_input("Company")
        location = c3.text_input("Location")
        url = st.text_input("Posting URL")
        description = st.text_area("Paste the job description *", height=250)
        if st.form_submit_button("Save job", type="primary"):
            if not title.strip() or not description.strip():
                st.error("Title and description are required.")
            else:
                db.add_job(title, company, location, url, description)
                st.success(f"Saved “{title}”.")
                st.rerun()

    if st.button("Load 5 sample internships", help="Adds example postings so you can try the dashboard."):
        for job in SAMPLE_JOBS:
            db.add_job(**job)
        st.rerun()

    st.subheader("Saved jobs")
    jobs_df = db.get_jobs()
    if jobs_df.empty:
        st.write("No jobs saved yet.")
    for _, job in jobs_df.iterrows():
        label = job["title"] + (f" — {job['company']}" if job["company"] else "")
        with st.expander(label):
            req, pref = split_required_preferred(job["description"])
            st.markdown("**Required skills detected:** " + badges(sorted(req), "blue"))
            st.markdown("**Preferred skills detected:** " + badges(sorted(pref), "gray"))
            with st.form(f"edit_{job['id']}"):
                c1, c2, c3 = st.columns(3)
                e_title = c1.text_input("Title", job["title"])
                e_company = c2.text_input("Company", job["company"] or "")
                e_location = c3.text_input("Location", job["location"] or "")
                e_url = st.text_input("URL", job["url"] or "")
                e_desc = st.text_area("Description", job["description"], height=200)
                b1, b2 = st.columns([1, 1])
                if b1.form_submit_button("Save changes"):
                    db.update_job(job["id"], e_title, e_company, e_location, e_url, e_desc)
                    st.rerun()
                if b2.form_submit_button("🗑️ Delete job"):
                    db.delete_job(job["id"])
                    st.rerun()

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
with tab_dash:
    jobs_df = db.get_jobs()
    if not resume:
        st.info("👈 Upload your resume in the sidebar to get started.")
    elif jobs_df.empty:
        st.info("Add some internships in the **Add / manage jobs** tab (or load the samples) to see rankings.")
    else:
        ranked = rank_jobs(resume, jobs_df)
        ranked["match"] = ranked["score"].apply(match_label)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Jobs compared", len(ranked))
        m2.metric("Best match", f"{ranked['score'].iloc[0]:.0f}%", ranked["title"].iloc[0], delta_color="off")
        m3.metric("Average score", f"{ranked['score'].mean():.0f}%")
        m4.metric("Strong / good matches", int((ranked["score"] >= 55).sum()))

        st.subheader("Ranked internships")
        table = ranked[["rank", "title", "company", "location", "score", "match", "skill_coverage",
                        "text_similarity", "missing_required"]].copy()
        table["missing_required"] = table["missing_required"].apply(lambda s: ", ".join(s) or "—")
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={
                "rank": st.column_config.NumberColumn("#", width="small"),
                "title": "Job title",
                "company": "Company",
                "location": "Location",
                "score": st.column_config.ProgressColumn("Match score", min_value=0, max_value=100, format="%.0f%%"),
                "match": "Fit",
                "skill_coverage": st.column_config.NumberColumn("Skill coverage", format="%.0f%%"),
                "text_similarity": st.column_config.NumberColumn("Text similarity", format="%.0f%%",
                                                                  help="TF-IDF cosine similarity (raw)"),
                "missing_required": st.column_config.TextColumn("Missing required skills", width="large"),
            },
        )
        st.download_button(
            "Download results as CSV",
            ranked.drop(columns=["description"]).to_csv(index=False),
            "internship_matches.csv",
            "text/csv",
        )

        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("Match scores")
            chart_df = ranked.assign(job=ranked["title"] + " (" + ranked["company"].fillna("") + ")")
            st.bar_chart(chart_df, x="job", y="score", horizontal=True, sort="-score", y_label="Match score (%)", x_label="")
        with c_right:
            st.subheader("Skills to learn next")
            st.caption("Skills missing from your resume, by how many saved jobs ask for them.")
            missing = pd.Series(
                [s for lst in ranked["missing_required"] + ranked["missing_preferred"] for s in lst],
                dtype="object",
            ).value_counts()
            if missing.empty:
                st.success("You cover every detected skill in your saved jobs. 🎉")
            else:
                missing_df = missing.head(10).rename_axis("skill").reset_index(name="jobs")
                st.bar_chart(missing_df, x="skill", y="jobs", horizontal=True, sort="-jobs", x_label="", y_label="Jobs requesting it")

        st.subheader("Job-by-job breakdown")
        for _, row in ranked.iterrows():
            head = f"#{row['rank']}  {row['title']}" + (f" — {row['company']}" if row["company"] else "")
            with st.expander(f"{head}  ·  {row['score']:.0f}% ({row['match']})"):
                st.progress(min(1.0, row["score"] / 100))
                if row["skill_coverage"] is None or pd.isna(row["skill_coverage"]):
                    st.caption("No known skills detected in this posting, so the score uses text similarity only.")
                st.markdown("✅ **Matched skills:** " + badges(row["matched_skills"], "green"))
                st.markdown("❌ **Missing required:** " + badges(row["missing_required"], "red"))
                st.markdown("➖ **Missing preferred:** " + badges(row["missing_preferred"], "orange"))
                st.markdown("🔑 **Other keywords in the posting not on your resume:** "
                            + badges(row["missing_keywords"], "gray"))
                if row["url"]:
                    st.markdown(f"[View posting]({row['url']})")
