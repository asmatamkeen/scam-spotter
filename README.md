# 🛡️ Scam Spotter

Fake internship offers are everywhere, and they're easy to fall for when you're a student looking for your first opportunity. Scam Spotter helps you check one before you pay or share anything.

Upload a screenshot or a PDF of a message or offer letter, and the app tells you if it looks safe, suspicious or a scam, and why.

Built for the Hacktoberfest Hack Day Hyderabad "Best Use of Gemma 4" challenge.

## What it does

- Reads screenshots and PDFs (offer letters, emails, WhatsApp messages)
- Gives a verdict: SAFE, SUSPICIOUS or SCAM, with a risk score out of 100
- Quotes the exact lines from the document that look like red flags
- Tells you what to do next
- Writes a ready-to-send WhatsApp alert so you can warn your friends in one tap

## How Gemma 4 is used

The uploaded image (or PDF pages converted to images) is sent to Gemma 4 (`gemma-4-31b-it`) through the Gemini API. Gemma reads the document, decides if it looks like a scam, and returns everything above. The app doesn't use keyword matching, so the verdict comes from Gemma's understanding of the document.

## Tech used

- Backend: Python, FastAPI
- Frontend: React (Vite)
- AI: Gemma 4 via the Gemini API

## How to run it

You need Python, Node.js and a free Gemini API key from [Google AI Studio](https://aistudio.google.com).

**1. Backend**

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On Mac/Linux, activate with `source venv/bin/activate` instead.

Create a `.env` file (see `.env.example`):

```
GEMINI_KEY=your_key_here
```

Start the server:

```
uvicorn main:app --reload
```

**2. Frontend** (open a second terminal)

```
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173

## Limitations

- It's an AI opinion, not a guarantee. Always double-check before trusting or rejecting an offer.
- Only the first 3 pages of a PDF are checked.
- Results can vary a little between runs.
- Built in a short hackathon, so there's no login, history or database.

## Made by

Asma