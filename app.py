import os
import re
import json
import pdfplumber
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from io import StringIO

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY is missing! Please set it in .env")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# AI Resume Analysis
def analyze_resume(resume_text, jd_text, detail_level: str = "Standard"):
    """Ask the model for strict JSON so we can parse reliably, with adjustable detail level."""
    # Detail configuration
    if detail_level == "Concise":
        note_len = "max 10 words"
        summary_sentences = "3 concise"
    elif detail_level == "Detailed":
        note_len = "15-25 words with specific evidence (projects, metrics if present)"
        summary_sentences = "6-7 rich"  # allow more depth
    else:  # Standard
        note_len = "8-15 words"
        summary_sentences = "4-5 balanced"

    prompt = (
        "You are an AI Resume Analyzer. Compare the RESUME with the JOB DESCRIPTION.\n"
        "Return ONLY valid minified JSON (no markdown fences, no commentary) using these keys: "
        "matched_skills:[{skill,note}], missing_skills:[{skill,note}], match_percentage:int (0-100), justification:str, summary:str.\n"
        f"For each matched_skills / missing_skills 'note' use {note_len}. Avoid repeating the skill name inside the note.\n"
        "Notes must explain relevance or gap (impact, context, or why important). No bullet symbols.\n"
        "match_percentage: integer (no % sign) reflecting how many required skills appear plus overall strength.\n"
        "justification: one sentence referencing strongest and most critical missing areas.\n"
        f"summary: {summary_sentences} sentences, professional tone, cover strengths, gaps, and actionable improvement suggestions.\n"
        "Do not include technologies in both matched and missing. Merge obvious synonyms.\n\n"
        f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}"
    )
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# Parse AI Response
def parse_response(raw_text):
    """Parse model output which should be JSON; fallback to regex if needed."""
    data = {
        "matched_skills": [],
        "missing_skills": [],
        "match_percentage": None,
        "justification": "",
        "summary": ""
    }

    # Attempt direct JSON load (strip possible markdown fences)
    cleaned = raw_text.strip().strip('`')
    fenced = re.sub(r'^json\n', '', cleaned, flags=re.IGNORECASE)
    try:
        parsed = json.loads(fenced)
        # Normalize keys in case of slight drift
        for k in data.keys():
            if k in parsed:
                data[k] = parsed[k]
        # Accept alternate key names
        if not data["match_percentage"]:
            mp_alt = parsed.get("matchPercent") or parsed.get("match_percentage") or parsed.get("match")
            data["match_percentage"] = mp_alt
    except Exception:
        # Fallback: extract sections heuristically
        def grab(sec):
            m = re.search(rf'{sec}:(.*?)(?:\n\n|$)', raw_text, flags=re.IGNORECASE|re.DOTALL)
            return m.group(1).strip() if m else ''
        matched_block = grab("Matched Skills")
        missing_block = grab("Missing Skills")
        pct_block = grab("Match Percentage")
        summary_block = grab("Summary") or grab("Overall")

        def to_list(block):
            items = []
            for line in block.splitlines():
                line=line.strip(" -*•\t")
                if not line:
                    continue
                items.append({"skill": line.split(":")[0].strip(), "note": ":".join(line.split(":")[1:]).strip() or ""})
            return items
        data["matched_skills"] = to_list(matched_block)
        data["missing_skills"] = to_list(missing_block)
        pct_num = re.search(r'(\d{1,3})\s*%?', pct_block)
        data["match_percentage"] = int(pct_num.group(1)) if pct_num else None
        data["justification"] = pct_block
        data["summary"] = summary_block

    # Post-process
    try:
        if data["match_percentage"] is not None:
            data["match_percentage"] = max(0, min(100, int(data["match_percentage"])))
    except Exception:
        data["match_percentage"] = None

    # Deduplicate skills & clean
    def clean_skill_list(lst):
        seen = set()
        cleaned = []
        for item in lst:
            if isinstance(item, str):
                skill = item.strip()
                note = ""
            else:
                skill = (item.get("skill") or "").strip()
                note = (item.get("note") or "").strip()
            key = skill.lower()
            if not skill or key in seen:
                continue
            seen.add(key)
            cleaned.append({"skill": skill, "note": note})
        return cleaned

    data["matched_skills"] = clean_skill_list(data["matched_skills"])
    data["missing_skills"] = clean_skill_list(data["missing_skills"])

    return data

def render_skill_list(skill_objs):
    if not skill_objs:
        return "<p>—</p>"
    lis = []
    for obj in skill_objs:
        skill = obj.get("skill", "").strip()
        note = obj.get("note", "").strip()
        if note and not note.endswith('.'):
            note += '.'
        text = f"<strong>{skill}</strong>" + (f": {note}" if note else "")
        lis.append(f"<li>{text}</li>")
    return "<ul>" + "".join(lis) + "</ul>"

# --- Streamlit UI ---
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="centered")

st.title("🤖 AI Resume Analyzer")
st.write("Upload your resume and job description. Choose detail level for the analysis.")

# Detail level control
detail_level = st.selectbox("Detail Level", ["Concise", "Standard", "Detailed"], index=1, help="Controls length of notes and summary depth")

# Job description input
jd_text = st.text_area("📄 Paste Job Description here:", height=150)

# Resume upload
uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf", "txt"])

if uploaded_file and jd_text:
    if st.button("🚀 Analyze Resume"):
        with st.spinner("Analyzing resume with AI... ⏳"):
            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = uploaded_file.read().decode("utf-8")
            raw = analyze_resume(resume_text, jd_text, detail_level)
            st.session_state["analysis_raw"] = raw
            st.session_state["analysis_parsed"] = parse_response(raw)
        st.success("✅ Analysis Complete!")

# Render if we have prior analysis
if "analysis_parsed" in st.session_state:
    parsed = st.session_state["analysis_parsed"]
    st.markdown(
        f"""
<div style="background:#1E1E1E; color:white; padding:20px; border-radius:15px; margin-top:20px;">
  <h3 style="color:#4CAF50;">🟢 Matched Skills</h3>
  {render_skill_list(parsed['matched_skills'])}
  <hr style="border:1px solid #444;">
  <h3 style="color:#FF9800;">🔴 Missing Skills</h3>
  {render_skill_list(parsed['missing_skills'])}
  <hr style="border:1px solid #444;">
  <h3 style="color:#2196F3;">📊 Match Percentage</h3>
  <p><b>{parsed['match_percentage'] if parsed['match_percentage'] is not None else 'N/A'}%</b> {parsed['justification']}</p>
  <hr style="border:1px solid #444;">
  <h3 style="color:#9C27B0;">📝 Summary</h3>
  <p>{parsed['summary']}</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    # --- Extra views & exports ---
    with st.expander("Raw JSON & Export"):
        col1, col2, col3 = st.columns(3)
        with col1:
            show_json = st.checkbox("Show Raw JSON", value=False)
        with col2:
            # Download JSON
            st.download_button(
                "Download JSON",
                data=json.dumps(parsed, indent=2),
                file_name="resume_analysis.json",
                mime="application/json",
            )
        with col3:
            # Markdown export
            md = [
                "# AI Resume Analysis",
                f"**Match Percentage:** {parsed['match_percentage']}%  ",
                f"_Justification:_ {parsed['justification']}",
                "\n## Matched Skills",
            ]
            for s in parsed['matched_skills']:
                md.append(f"- **{s['skill']}**: {s['note']}")
            md.append("\n## Missing Skills")
            for s in parsed['missing_skills']:
                md.append(f"- **{s['skill']}**: {s['note']}")
            md.append("\n## Summary\n" + parsed['summary'])
            md_text = "\n".join(md)
            st.download_button(
                "Download Markdown",
                data=md_text,
                file_name="resume_analysis.md",
                mime="text/markdown",
            )
        if show_json:
            st.code(json.dumps(parsed, indent=2), language="json")
