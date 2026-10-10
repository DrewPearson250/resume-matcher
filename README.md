Find opportunities. Discover skill gaps. Build your career.

A Python-powered application that helps students identify relevant internships by comparing resumes with job descriptions using natural language processing (NLP) and text similarity techniques.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Machine%20Learning-Scikit--learn-orange?logo=scikitlearn&logoColor=white" alt="Scikit-learn"/>
  <img src="https://img.shields.io/badge/Status-Finished-green" alt="Finished"/>
</p>

📌 Table of Contents

Overview

Features

How It Works

Tech Stack

Getting Started

Project Structure

Future Improvements

Disclaimer

🎯 Overview

Finding the right internship can be difficult, especially for students starting their careers in technology.

AI-Powered Job & Internship Matcher is designed to make the search process more efficient by analyzing resume content and comparing it with internship requirements. It helps users understand how closely their experience aligns with a position and identify skills they may want to develop.

The goal is to turn a time-consuming job search into a more organized, data-driven experience.

✨ Features

Feature

Description

📄 Resume Analysis

Upload a PDF resume and extract its text for analysis.

🎯 Compatibility Scoring

Calculate resume-to-job-description similarity scores.

🧠 NLP Matching

Use TF-IDF and cosine similarity to compare relevant text.

🔍 Skill Gap Analysis

Identify job-related skills that may be missing from a resume.

📊 Interactive Dashboard

Display matching results and insights in a user-friendly interface.

💾 Saved Opportunities

Store and retrieve job listings using SQLite.

Features listed above represent the planned functionality. Update this table as each feature is implemented.

<img width="1512" height="827" alt="Screenshot 2026-10-09 at 9 13 42 PM" src="https://github.com/user-attachments/assets/a3252187-e9fb-4ef8-b26a-57145edfdbaa" />


⚙️ How It Works

<p align="center">
  <strong>Upload Resume</strong> → <strong>Enter Job Description</strong> → <strong>Analyze Text</strong> → <strong>Review Match Results</strong>
</p>

1. Upload a resume

The user provides a PDF resume containing education, experience, projects, and technical skills.

2. Enter a job description

The user pastes the description of a software engineering internship or other job opportunity.

3. Analyze the text

The application processes both documents and uses TF-IDF to represent their text numerically.

4. Calculate similarity

Cosine similarity measures how closely the resume and job description match in terms of their text.

5. Review the results

The user reviews the compatibility score and, when implemented, relevant skill gaps and saved opportunities.

Important: A similarity score measures textual overlap, not the probability of receiving an interview or job offer.

🛠️ Tech Stack

Technology

Purpose

Python

Core application logic and text processing

Streamlit

Interactive web application interface

Scikit-learn

TF-IDF vectorization and cosine similarity

Pandas

Data organization and processing

SQLite

Local storage for saved opportunities

PyMuPDF

PDF text extraction

🚀 Getting Started

Follow these steps to run the project locally.

Prerequisites

Python 3.10 or later

Git

pip

1. Clone the repository

Replace the example URL with your actual GitHub repository URL.

git clone YOUR_GITHUB_REPOSITORY_URL

2. Navigate to the project folder

cd ai-internship-matcher

3. Create a virtual environment

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate

Windows

python -m venv .venv
.venv\Scripts\activate

4. Install dependencies

pip install -r requirements.txt

5. Launch the application

streamlit run app.py

Open the local URL shown in your terminal to access the application.

📂 Project Structure

A suggested organization for the project:

ai-internship-matcher/
│
├── app.py                 # Streamlit application
├── matcher.py             # Text similarity and matching logic
├── resume_parser.py       # Resume PDF processing
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Files excluded from Git
└── screenshots/
    └── dashboard.png      # Application screenshot

The structure can change as the application develops. Only include files that exist in your repository.

🔮 Future Improvements

Integrate a job listings API to retrieve internship opportunities.

Improve skill extraction with advanced NLP models.

Add filters for location, job title, and required technologies.

Build a personalized dashboard for saved internships.

Add automated tests for matching and document processing.

Deploy the application using Streamlit Community Cloud.

🎓 Learning Objectives

This project explores practical software development concepts, including:

Python programming and modular application design

Natural language processing and text similarity

Data processing and analysis

Database integration and data persistence

User interface development

Testing, debugging, and technical documentation

⚠️ Disclaimer

This application is intended for educational and career-planning purposes. Matching scores are estimates based on textual similarity and should not be treated as definitive assessments of a candidate's qualifications.

👨‍💻 Author

Drew Pearson

Computer Science Student

GitHub Profile

<p align="center">
  <i>Built to make the internship search more organized, transparent, and data-driven.</i>
</p>
# resume-matcher
