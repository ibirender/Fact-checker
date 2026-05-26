# FactGuard AI 🔍

An AI-powered **Fact-Checking Web App** that automatically verifies claims in PDF documents using Groq's Llama 3.3 70B model.

## 🚀 Live Demo
https://factguard-ai-2etssbphxqcr2ppfxjitnd.streamlit.app/

## ✨ Features
- 📄 Upload any PDF document
- 🤖 AI extracts all verifiable claims (stats, dates, figures)
- 🌐 Cross-references claims against Llama 3.3's knowledge base
- 🚨 Flags claims as **Verified** ✅, **Inaccurate** ⚠️, or **False** ❌
- 📊 Summary dashboard with claim breakdown
- 📜 History tracking of all analyses
- 📥 Export reports as JSON

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI Engine:** Groq (Llama 3.3 70B)
- **PDF Parsing:** PyMuPDF (fitz)
- **Deployment:** Streamlit Cloud
- **Language:** Python

## 📦 Installation (Local)

```bash
git clone https://github.com/Yash8439/factguard-ai
cd factguard-ai
pip install -r requirements.txt
streamlit run app.py
🔑 API Keys Required
Service	Purpose	Get Here
Groq API	LLM for claim extraction & analysis	console.groq.com
Tavily API	Live web search for verification	tavily.com
Free Tier Limits:

Groq: 30 requests/minute

Tavily: 1000 searches/month

📋 How It Works
text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Upload    │────▶│   Extract   │────▶│  Web Search │────▶│   Report    │
│     PDF     │     │   Claims    │     │  (Tavily)   │     │  Results    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                    │                    │
                           ▼                    ▼                    ▼
                    Stats, Dates,          Live fact            Verified ✅
                    Financial data         checking             Inaccurate ⚠️
                                                                False ❌
Step-by-Step Process:
Upload PDF - User uploads marketing content, reports, or articles

Extract Text - PyMuPDF parses and extracts all readable text

Identify Claims - Groq LLM extracts specific verifiable claims (statistics, dates, figures)

Live Web Search - Tavily API searches the web for current facts

Analyze & Verify - Groq compares claims against search results

Display Results - Shows classification with explanations and sources

🧪 Test Results (Trap Document)
Test Document: COVID-19 Myths PDF (published 2020)

Claim	Expected	Actual Result
"No drug to prevent/treat COVID"	INACCURATE	✅ INACCURATE - Treatments now exist (2024)
"Garlic prevents COVID"	VERIFIED	✅ VERIFIED - No scientific evidence
"UV bulbs can be used on body"	VERIFIED	✅ VERIFIED - UV harmful to skin
"Saline rinse prevents COVID"	VERIFIED	✅ VERIFIED - No preventive effect
✅ Success Criteria Met: App successfully flagged outdated claim and provided correct real facts.

📊 Sample Output
text
📊 SUMMARY
├── Total Claims: 10
├── Verified: 9 ✅
├── Inaccurate: 1 ⚠️
└── False: 0 ❌

🔎 DETAILED RESULTS

⚠️ INACCURATE
"At present, there is no drug that can prevent and treat the disease"
→ This claim is outdated. Several treatments including Paxlovid, 
  Remdesivir, and vaccines have been developed since 2020.
📎 Sources: fda.gov | who.int

✅ VERIFIED
"Eating garlic does not prevent COVID-19"
→ Verified: No scientific evidence supports this claim.
📎 Sources: who.int | cdc.gov
📁 Project Structure
text
factguard-ai/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
└── .streamlit/
    └── secrets.toml      # API keys (git-ignored)
🔧 Environment Variables (Streamlit Secrets)
toml
GROQ_API_KEY = "your_groq_api_key_here"
TAVILY_API_KEY = "your_tavily_api_key_here"
📈 Future Enhancements
Support for DOCX, TXT files

Multiple language support

Real-time web search with more sources

PDF highlighting of problematic claims

Batch document processing

Export to CSV/Excel

🎯 Evaluation Criteria (How This App Meets Requirements)
Requirement	Implementation
Extract claims from PDF	PyMuPDF + Groq LLM
Verify against live web data	Tavily API real-time search
Flag as Verified/Inaccurate/False	3-tier classification system
Deployed web app	Streamlit Cloud (live URL)
Provide correct real facts	Groq analyzes search results
Demo video	30-second screen recording
🎥 Demo Video
[Link to 30-second demo video]

Video demonstrates: PDF upload → Claim extraction → Live web search → Outdated claim flagged → Correct fact displayed

👨‍💻 Author
Yash
Product Management Trainee Candidate
Cog Culture Assessment

https://github.com/Yash8439/factguard-ai/edit/main/README.md
https://www.linkedin.com/in/yash-rastogi-80a84b28b/

📄 License
MIT License - Free for educational and evaluation purposes.

🙏 Acknowledgments
Groq for high-speed LLM inference

Tavily for real-time web search API

Streamlit for easy deployment

Built with ❤️ for Cog Culture Product Management Trainee Assessment






