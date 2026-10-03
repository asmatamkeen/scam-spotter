import os
import json
import pymupdf
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

MODEL = "gemma-4-31b-it"

PROMPT = """You are a scam detector helping Indian college students.
Look at this screenshot or document (message, email, or job/internship offer).
Only flag clear scam signs. A normal, professional offer should be SAFE.
Reply with ONLY valid JSON, no extra text, in this format:
{
  "verdict": "SAFE" or "SUSPICIOUS" or "SCAM",
  "risk_score": a number from 0 to 100,
  "summary": "one simple sentence",
  "red_flags": [
    {"flag": "short reason", "quote": "exact words from the document"}
  ],
  "what_to_do": "one clear next step",
  "warning_message": "A WhatsApp alert to forward to friends. Use this exact structure, with \\n for new lines: '⚠️ *SCAM ALERT*\\n\\n*What:* one line on what the message/offer claims to be (include the company or sender name if visible)\\n*The trap:* what they ask for (include the amount, link, or personal details asked for)\\n*Why it's fake:* 1-2 short reasons\\n*What to do:* one short action\\n\\nChecked with Scam Spotter (Gemma 4)'. Use only details actually visible in the document. Use wording like 'looks like a scam' instead of stating it as proven fact. Leave empty if SAFE."
}
If there are no red flags, return an empty list.
Use very simple English."""

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def pdf_to_parts(data, max_pages=3):
    doc = pymupdf.open(stream=data, filetype="pdf")
    parts = []
    for i in range(min(len(doc), max_pages)):
        pix = doc[i].get_pixmap(dpi=120)
        parts.append(types.Part.from_bytes(data=pix.tobytes("png"), mime_type="image/png"))
    return parts


@app.post("/check")
async def check(file: UploadFile = File(...)):
    data = await file.read()
    if file.content_type == "application/pdf":
        parts = pdf_to_parts(data)
    else:
        parts = [types.Part.from_bytes(data=data, mime_type=file.content_type)]
    try:
        response = client.models.generate_content(model=MODEL, contents=parts + [PROMPT])
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}