import os
import io
import json
import time
import pymupdf
from PIL import Image
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from datetime import date

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

MODEL = "gemma-4-31b-it"

PROMPT = """You are a scam detector helping Indian college students.
Look at this screenshot or document (message, email, or job/internship offer or joining letter).

Today's date is TODAY_DATE. Dates on or before today are in the past. Do NOT flag a date as "future" or "in the future" unless it is after today's date. A document dated in the past is normal.

Be careful and fair. Real companies often include normal things in joining letters: joining date, stipend, working hours, confidentiality or notice-period terms, and an HR contact. These are NOT red flags.

Clear scam signs are: asking the candidate to pay money (registration, training, security deposit, laptop or kit fee), asking for bank details or OTP, free email addresses (Gmail, Yahoo) used as the official company address, urgent pressure to respond, or a job offered with no interview.

Use SCAM only when there is a clear scam sign from that list. Use SUSPICIOUS when something is unusual but not clearly a scam. Use SAFE when none of the clear signs are present.

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


def shrink_image(data, max_size=1280):
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((max_size, max_size))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return buf.getvalue()


def pdf_to_parts(data, max_pages=2):
    doc = pymupdf.open(stream=data, filetype="pdf")
    parts = []
    for i in range(min(len(doc), max_pages)):
        pix = doc[i].get_pixmap(dpi=100)
        parts.append(types.Part.from_bytes(data=pix.tobytes("png"), mime_type="image/png"))
    return parts


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in: " + text[:200])
    return json.loads(text[start:end + 1])


@app.post("/check")
async def check(file: UploadFile = File(...)):
    data = await file.read()
    if file.content_type == "application/pdf":
        parts = pdf_to_parts(data)
    else:
        parts = [types.Part.from_bytes(data=shrink_image(data), mime_type="image/jpeg")]

    last_error = ""
    prompt = PROMPT.replace("TODAY_DATE", date.today().strftime("%d %B %Y"))
    for attempt in range(3):
        try:
            start = time.time()
            response = client.models.generate_content(
                model=MODEL,
                contents=parts + [PROMPT],
                config=types.GenerateContentConfig(temperature=0),
            )
            print("Gemma took:", round(time.time() - start, 1), "seconds")
            return extract_json(response.text)
        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt + 1} failed:", last_error)
            time.sleep(2)
    return {"error": last_error}