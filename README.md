# AI Quiz Generator from Study Notes

## Features
- Admin login controlled by `.env`
- Upload multiple text-based PDF/TXT files
- Subject-wise study material library
- Generate MCQs from selected notes using the OpenAI Responses API
- Multiple independent Streamlit student sessions
- Countdown timer with automatic submission when the active page is running
- Marks, percentage, answer review and explanations
- Exam-wise leaderboard (best attempt per student) and CSV downloads
- SQLite persistence for local testing

## Windows / VS Code setup
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
4. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
5. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. Copy `.env.example` to a new file named `.env`. In VS Code, you can right-click `.env.example`, choose Copy, then paste and rename it `.env`.
7. Add your own API key to `OPENAI_API_KEY`, and set a unique `ADMIN_PASSWORD`. Do not include quotes around the values unless needed.
8. Run:
   ```powershell
   python -m streamlit run app.py
   ```
9. Open the local URL printed by Streamlit, usually http://localhost:8501.

## API key safety
- Create a key in the OpenAI API platform. API usage is separate from a ChatGPT subscription and may incur charges.
- Keep the key only in `.env` or your deployment's secret settings.
- Never paste the key into `app.py`, screenshots, public GitHub, or chat messages.
- `.gitignore` excludes `.env`. Before pushing to GitHub, confirm it is not tracked with `git status`.
- If a key is exposed, revoke it and create a new one.

## Admin usage
1. Sign in with `ADMIN_USERNAME` and `ADMIN_PASSWORD` from `.env`.
2. Open **Upload notes** and choose a subject.
3. Select multiple PDF/TXT files and save them.
4. Open **Create exam**, choose a subject and one or more materials, set exam title, question count and duration, then generate the exam.
5. Students select the exam under **Student Exams**.

## Important limitations
- This is a college project/demo, not a secure high-stakes examination platform.
- Student names are not identity verification; students can enter the same name. Add accounts and attempt controls before real use.
- The countdown and automatic submission run while the student's Streamlit page/session is active. Browser closure or network loss may prevent the UI from submitting at the exact deadline. A production exam system needs server-side expiry enforcement and persistent attempts.
- Local SQLite and uploaded materials live on the server filesystem. Many simultaneous users on one machine can work for a demo, but for a public/cloud deployment use a managed PostgreSQL database and persistent file storage.
- Text-based PDFs are supported. Image-only scanned PDFs need OCR.
- The app sends extracted notes to the selected AI API to generate questions. Do not upload confidential material unless you are authorized to share it.
- AI output can be wrong. Admins should review generated questions before students take the exam.
- The default model is `gpt-5.5`; if your API account does not have access to that model, change `OPENAI_MODEL` in `.env` to a model available to your API account.
