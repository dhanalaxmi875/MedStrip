# 💊 MedStrip - AI Medicine Strip Scanner & Schedule Assistant

An intelligent AI-powered medicine strip scanner and dosage scheduler built with **Streamlit** and **Google Gemini Vision**.

MedStrip reads photos of medicine packaging, extracts active ingredients, dosage forms, and strengths with strict hallucination guards, validates the readability, and generates an easy-to-read daily schedule that patients or caregivers can download or send directly to WhatsApp.

---

## ✨ Features

- **🔍 Smart Strip Vision Extraction:** Powered by Google Gemini (`gemini-3.8-flash` with automatic fallback to `gemini-flash-latest`) using structured Pydantic schemas.
- **🛡️ Strict Anti-Hallucination & Legibility Triage:** Only extracts physically printed and legible text. Clearly flags unreadable parts, missing strengths, or low-quality photos.
- **⏰ Interactive Dosage Scheduler:** Customize schedules for Morning, Afternoon, Evening, and Night, including meal timings (Before / After food).
- **💬 1-Click WhatsApp Sharing:** Generates patient-ready reminder text and opens directly in WhatsApp with pre-filled messages.
- **📥 Offline Download:** Export schedules as clean `.txt` files.
- **🎨 Polished UI:** Streamlit interface with a custom teal theme, progress trackers, and safety badges.

---

## 📁 Project Structure

```text
MedStrip/
├── .streamlit/
│   └── config.toml        # Custom Streamlit UI theme configuration
├── app.py                 # Main Streamlit web application
├── extractor.py           # Gemini vision extraction with Pydantic JSON schema
├── gemini_client.py       # Gemini API client with fallback and exponential backoff
├── schema.py              # Pydantic data models (Medicine, ScanResult)
├── validator.py           # Safety validation and triage rules
├── test_vision.py         # CLI test utility for sample image scanning
├── requirements.txt       # Project dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignore configuration
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/MedStrip.git
cd MedStrip
```

### 2. Set Up a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and add your **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/):
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 💻 Running the Application

Launch the Streamlit app:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

### CLI Testing (Optional)

You can also test extraction directly from the command line on any image:

```bash
python test_vision.py path/to/medicine_strip.jpg
```

---

## 📦 Requirements

- Python 3.10+
- `streamlit`
- `google-genai`
- `pillow`
- `python-dotenv`
- `pydantic`

---

## 🔒 Security & Privacy

- Medicine photos and patient data are processed via API calls and are not stored permanently.
- Never commit your `.env` file to source control. It is ignored by default in `.gitignore`.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
