from flask import Flask, render_template, request # Flask is a python framework used to create web application
from PyPDF2 import PdfReader
import ollama

app = Flask(__name__) # __name__ tells Flask where the application is located

SKILLS = [
    "Python", 
    "Java", 
    "HTML", 
    "CSS", 
    "JavaScript",
    "SQL", 
    "Flask",
    "Git",
    "GitHub",
    "React",
    "Machine Learning",
    "Data Science"
]

@app.route("/") # When someone visits the main URL /, run the function below
def home():
    return render_template("index.html")

@app.route("/analyze", methods = ["POST"])
def analyze():
    resume = request.files["resume"]

    job_role = request.form["job_role"]

    if resume.filename == "":
        return render_template(
            "index.html",
            error = "Please select a resume file."
        )

    if not resume.filename.lower().endswith(".pdf"):
        return render_template(
            "index.html",
            error = "Please upload a PDF file."
        )

    reader = PdfReader(resume)

    resume_text = ""

    for page in reader.pages:
        resume_text += page.extract_text() or ""

    page_count = len(reader.pages)
    word_count = len(resume_text.split())

    found_skills = []

    for skill in SKILLS:
        if skill.lower() in resume_text.lower():
            found_skills.append(skill)

    missing_skills = []

    for skill in SKILLS:
        if skill not in found_skills:
            missing_skills.append(skill)

    score = int((len(found_skills) / len(SKILLS)) * 100)

    try:
        ai_response = ollama.chat(
            model = "llama3.2:3b",
            messages = [
                {
                    "role": "user",
                    "content": f"""
    Analyze this resume specifically for the target job role: {job_role}

    Resume:
    {resume_text}

    Provide:
    1. Main strengths relevent to the target job
    2. Weak areas fo this target job
    3. Specific improvement suggestions
    4. Important missing keywords or skills for this target job
    5. Overall suitability for the target job
    6. List 10 important technical skills or keywords tha are commonly expected for this target job
    """
                }
            ]
        )

        ai_analysis = ai_response["message"]["content"]

    except Exception:
        ai_analysis = (
            "AI analysis is currently unavailable. "
            "Please make sure Ollama is running and try again."
        )

    if score >= 80:
        strength = "Strong skill coverage"
    elif score >= 60:
        strength = "Good, but can be improved"
    else:
        strength = "Needs improvement"

    return render_template(
        "result.html",
        score = score,
        strength = strength,
        found_skills = found_skills,
        missing_skills = missing_skills,
        page_count = page_count,
        word_count = word_count,
        ai_analysis = ai_analysis,
        job_role = job_role
    )

    
if __name__ == "__main__": # Are we running app.py directly? if yes, run the code below
    app.run(debug = True)