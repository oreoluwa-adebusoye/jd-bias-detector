# Bias Detector for Job Descriptions

An **AI + NLP tool** that scans job descriptions for biased or exclusionary language, highlights problematic terms, and suggests inclusive alternatives. Built with Python, Streamlit, and optional zero-shot ML classification.

---

## 🚀 Features
- **Paste or Upload** a job description (`.txt`, `.pdf`, `.docx`)
- **Rule-based detection** for common biased phrases  
  *(e.g., “rockstar,” “aggressive,” “digital native”)*
- **Optional ML mode** using zero-shot classification for nuanced bias detection
- **Bias Score** from 0–100 (lower = more bias)
- **Category counts** (e.g., gender-coded, age-coded, ableist)
- **Highlighting** in text with color-coded categories *(coming soon)*
- **Rewrite suggestions** for flagged terms

---

## 🛠️ Tech Stack
- **Backend**: Python, spaCy, NLTK, scikit-learn
- **ML (optional)**: Hugging Face Transformers (zero-shot classification)
- **Frontend**: Streamlit
- **File parsing**: pdfplumber, python-docx

---

## 📦 Installation

Clone the repo:
```bash
git clone https://github.com/YOUR-USERNAME/bias-detector.git
cd bias-detector

Create a virtual environment and install dependencies:
python -m venv .venv
source .venv/bin/activate    # on macOS/Linux
.venv\Scripts\activate       # on Windows
pip install -r requirements.txt

```
## Usage
Run the app:
```streamlit run app.py```
Then open the local URL in your browser.

## How It Works
1. Rule-Based Pass → Scans text for regex patterns of biased terms.
2. ML Pass (optional) → Uses a zero-shot classifier to detect subtler bias.
3. Bias Score → Weighted scoring system based on number and severity of matches.
4. Suggestions → Inclusive language alternatives for flagged terms.

## 📌 Roadmap
 - Color-coded category highlights
 -  Downloadable PDF/CSV reports
 -   Multi-language support
 -   Batch scan for multiple job postings

## 🤝 Contributing
Pull requests are welcome! Please fork the repo and submit a PR with clear commit messages.

## 📜 License
MIT License – feel free to use and adapt this project.

