
import streamlit as st
import fitz
import random
import time
import json
import os
import pandas as pd
from pathlib import Path

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="📝",
    layout="wide"
)

DB_FILE = "quiz_results.json"
NOTES_DIR = Path("uploaded_notes")
NOTES_DIR.mkdir(exist_ok=True)

if "materials" not in st.session_state:
    st.session_state.materials = []

if "exam" not in st.session_state:
    st.session_state.exam = None

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "student_name" not in st.session_state:
    st.session_state.student_name = ""

if "results" not in st.session_state:
    if os.path.exists(DB_FILE):
        try:
            st.session_state.results = json.loads(
                Path(DB_FILE).read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            st.session_state.results = []
    else:
        st.session_state.results = []


def save_results():
    Path(DB_FILE).write_text(
        json.dumps(st.session_state.results, indent=2),
        encoding="utf-8"
    )


def extract_pdf_text(uploaded_file):
    document = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
    text = "\n".join(page.get_text() for page in document)
    document.close()
    return text.strip()


def make_questions(text, count):
    """Create simple text-based questions from extracted PDF sentences."""
    sentences = [
        s.strip()
        for s in text.replace("\n", " ").split(".")
        if len(s.strip().split()) >= 5
    ]

    if not sentences:
        return []

    random.shuffle(sentences)
    questions = []

    for sentence in sentences[:count]:
        correct = sentence.strip()
        words = correct.split()
        blank_index = max(0, min(len(words) - 1, len(words) // 2))
        answer = words[blank_index].strip(" ,;:")

        if len(answer) < 2:
            continue

        words[blank_index] = "________"
        question_text = " ".join(words)

        distractors = list({
            word.strip(" ,;:.")
            for word in text.split()
            if word.strip(" ,;:.").isalpha()
            and word.strip(" ,;:.").lower() != answer.lower()
            and len(word.strip(" ,;:.")) > 2
        })

        random.shuffle(distractors)
        options = [answer] + distractors[:3]
        options = list(dict.fromkeys(options))

        if len(options) < 2:
            continue

        random.shuffle(options)

        questions.append({
            "question": f"Complete the statement: {question_text}",
            "options": options,
            "answer": answer,
            "explanation": f"Source statement: {correct}"
        })

    return questions


# ---------------- HEADER ----------------
st.title("📝 AI Quiz Generator from Study Notes")
st.write(
    "Upload your study PDF, create a quiz, set an exam time limit, "
    "and view student marks and rankings."
)

upload_tab, exam_tab, results_tab = st.tabs([
    "📚 Upload PDF & Generate Quiz",
    "🎓 Student Exam",
    "🏆 Results & Graphs"
])

# ---------------- UPLOAD PDF & CREATE QUIZ ----------------
with upload_tab:
    st.header("📚 Upload Study Material")

    pdf_file = st.file_uploader(
        "Choose your study PDF file",
        type=["pdf"],
        key="pdf_upload"
    )

    material_title = st.text_input(
        "Study material title",
        placeholder="Example: Python Programming Notes"
    )

    subject = st.selectbox(
        "Select subject",
        ["Python", "Artificial Intelligence", "DBMS",
         "Web Development", "Java", "Other"]
    )

    if st.button("📤 Upload PDF and Save Notes", type="primary"):
        if pdf_file is None:
            st.error("Please choose a PDF file first.")
        else:
            try:
                pdf_text = extract_pdf_text(pdf_file)

                if len(pdf_text) < 30:
                    st.error(
                        "Very little text was extracted. "
                        "This PDF may contain scanned images."
                    )
                else:
                    filename = NOTES_DIR / Path(pdf_file.name).name
                    filename.write_bytes(pdf_file.getvalue())

                    material = {
                        "title": material_title.strip()
                        or pdf_file.name,
                        "subject": subject,
                        "filename": pdf_file.name,
                        "text": pdf_text
                    }

                    st.session_state.materials.append(material)
                    st.success("PDF uploaded and text extracted successfully!")
                    st.info(f"Extracted {len(pdf_text)} characters.")
            except Exception as error:
                st.error(f"Could not read this PDF: {error}")

    st.divider()
    st.header("🧠 Generate Quiz")

    if not st.session_state.materials:
        st.info("Upload a PDF above before generating a quiz.")
    else:
        material_labels = [
            f'{m["title"]} — {m["subject"]}'
            for m in st.session_state.materials
        ]

        selected_index = st.selectbox(
            "Choose uploaded study material",
            range(len(material_labels)),
            format_func=lambda i: material_labels[i]
        )

        exam_title = st.text_input(
            "Exam name",
            value="Practice Examination"
        )

        col1, col2 = st.columns(2)

        with col1:
            question_count = st.number_input(
                "Number of questions",
                min_value=1,
                max_value=30,
                value=5
            )

        with col2:
            duration = st.number_input(
                "Exam time limit (minutes)",
                min_value=1,
                max_value=180,
                value=10
            )

        if st.button("✨ Generate Quiz", type="primary"):
            material = st.session_state.materials[selected_index]
            questions = make_questions(
                material["text"], int(question_count)
            )

            if not questions:
                st.error(
                    "Could not create questions from this PDF. "
                    "Try a PDF containing selectable text."
                )
            else:
                st.session_state.exam = {
                    "title": exam_title,
                    "subject": material["subject"],
                    "questions": questions,
                    "duration": int(duration)
                }
                st.session_state.answers = {}
                st.success(
                    f"Quiz created successfully with "
                    f"{len(questions)} questions!"
                )
                st.info("Open the Student Exam tab to take the quiz.")

# ---------------- STUDENT EXAM ----------------
with exam_tab:
    st.header("🎓 Student Examination")

    exam = st.session_state.exam

    if exam is None:
        st.warning(
            "No quiz has been created yet. Go to "
            "'Upload PDF & Generate Quiz' first."
        )
    else:
        name = st.text_input(
            "Enter your name",
            value=st.session_state.student_name,
            placeholder="Enter student name"
        )

        if st.button("Start / Restart Exam"):
            if not name.strip():
                st.error("Please enter your name.")
            else:
                st.session_state.student_name = name.strip()
                st.session_state.answers = {}
                st.session_state.exam_started = time.time()
                st.session_state.exam_deadline = (
                    time.time() + exam["duration"] * 60
                )
                st.session_state.exam_active = True
                st.rerun()

        if st.session_state.get("exam_active", False):
            remaining = max(
                0, int(st.session_state.exam_deadline - time.time())
            )

            st.subheader(f"Exam: {exam['title']}")
            st.write(f"Student: {st.session_state.student_name}")
            st.metric(
                "Time remaining",
                f"{remaining // 60:02d}:{remaining % 60:02d}"
            )

            if remaining <= 0:
                st.warning("Time is up! Submit your exam now.")
            else:
                st.caption(
                    "The timer is checked when the app reruns. "
                    "Submit before the deadline."
                )

            with st.form("exam_answer_form"):
                chosen_answers = {}

                for i, question in enumerate(exam["questions"]):
                    st.markdown(
                        f"**Question {i + 1}. "
                        f"{question['question']}**"
                    )
                    chosen_answers[i] = st.radio(
                        "Select your answer",
                        ["— Select an answer —"] + question["options"],
                        key=f"answer_{i}"
                    )

                submitted = st.form_submit_button("Submit Exam")

            if submitted or remaining <= 0:
                score = 0
                details = []

                for i, question in enumerate(exam["questions"]):
                    selected = chosen_answers.get(i, "— Select an answer —")
                    correct = question["answer"]
                    is_correct = selected.lower() == correct.lower()

                    if is_correct:
                        score += 1

                    details.append({
                        "Question": question["question"],
                        "Your answer": selected,
                        "Correct answer": correct,
                        "Result": "Correct" if is_correct else "Incorrect"
                    })

                total = len(exam["questions"])
                percentage = round(score / total * 100, 2) if total else 0

                st.session_state.results.append({
                    "Student": st.session_state.student_name,
                    "Exam": exam["title"],
                    "Subject": exam["subject"],
                    "Marks": score,
                    "Total": total,
                    "Percentage": percentage,
                    "Date": time.strftime("%Y-%m-%d %H:%M")
                })
                save_results()

                st.session_state.last_result = {
                    "score": score,
                    "total": total,
                    "percentage": percentage,
                    "details": details
                }
                st.session_state.exam_active = False
                st.rerun()

        if st.session_state.get("last_result"):
            result = st.session_state.last_result
            st.divider()
            st.subheader("📊 Your Examination Result")
            c1, c2, c3 = st.columns(3)
            c1.metric("Marks", f"{result['score']}/{result['total']}")
            c2.metric("Percentage", f"{result['percentage']}%")
            c3.metric(
                "Status",
                "Pass" if result["percentage"] >= 40 else "Needs Improvement"
            )

            st.bar_chart(pd.DataFrame({
                "Marks": [result["score"],
                          result["total"] - result["score"]]
            }, index=["Correct", "Incorrect"]))

            st.write("### Detailed answers")
            st.dataframe(
                pd.DataFrame(result["details"]),
                use_container_width=True
            )

# ---------------- RESULTS AND GRAPHS ----------------
with results_tab:
    st.header("🏆 Student Rankings & Results")

    if not st.session_state.results:
        st.info("No exam results available yet.")
    else:
        df = pd.DataFrame(st.session_state.results)
        st.subheader("All Student Results")
        st.dataframe(df, use_container_width=True)

        st.subheader("🏅 Student Ranking")
        ranking = (
            df.sort_values(
                ["Percentage", "Marks"],
                ascending=[False, False]
            )
            .reset_index(drop=True)
        )
        ranking.insert(0, "Rank", range(1, len(ranking) + 1))
        st.dataframe(
            ranking[["Rank", "Student", "Exam", "Marks", "Total", "Percentage"]],
            use_container_width=True
        )

        st.subheader("📈 Student Marks Graph")
        chart_df = df.groupby("Student")["Marks"].max().sort_values(
            ascending=False
        )
        st.bar_chart(chart_df)

        st.subheader("📊 Average Percentage")
        st.bar_chart(df.groupby("Exam")["Percentage"].mean())

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Results CSV",
            data=csv_data,
            file_name="quiz_results.csv",
            mime="text/csv"
        )

st.divider()
st.caption("AI Quiz Generator from Study Notes | BCA Mini Project")
