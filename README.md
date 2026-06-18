# The Fact-Check Agent (Vercel build)

A FastAPI app, single-page frontend included, built specifically for native
Vercel deployment. Upload a PDF, it extracts checkable claims (stats, dates,
financial/technical figures), searches the live web for each one, and
stamps a verdict: **Verified**, **Inaccurate**, or **False** — with the
correct fact and sources.

Built for the CogCulture Product Management Trainee assessment (Part 2).

## Why this structure

Vercel has zero-config support for FastAPI: a top-level `app` instance in
`app.py` is auto-detected and deployed as a Vercel Function, with all
routes (`/`, `/api/extract`, `/api/verify`) handled by the same app. No
separate Next.js/React build step, no `vercel.json` rewrites needed.

```
.
├── app.py                   # FastAPI app: routes + inlined HTML/CSS/JS frontend
├── pdf_utils.py              # PDF text extraction (pypdf — pure Python, no native deps)
├── claim_extractor.py        # Claim extraction via Claude
├── web_verifier.py           # Live DuckDuckGo search + verdict via Claude
├── make_sample_trap_pdf.py   # Regenerates the test PDF below
├── sample_trap_document.pdf  # Pre-built test PDF with planted false/outdated stats
├── requirements.txt
├── vercel.json                # Extends function timeout to 60s for slower PDFs
└── .env.example
```

## 1. Run it locally first

```bash
git clone <your-repo-url>
cd factcheck-vercel
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your real Anthropic API key

export $(grep -v '^#' .env | xargs)
uvicorn app:app --reload
```

Open `http://localhost:8000`, upload `sample_trap_document.pdf`, and confirm
the agent catches the planted false/outdated claims before you deploy.

## 2. Deploy to Vercel

```bash
npm i -g vercel        # if you don't have the CLI yet
vercel login
vercel                 # first deploy, links/creates the project, deploys a preview
```

Then add your API key as a secret (do this in the dashboard, never commit it):

1. Go to your project on vercel.com -> **Settings -> Environment Variables**.
2. Add `ANTHROPIC_API_KEY` = your real key, for Production (and Preview if you want).
3. Redeploy so the function picks up the new variable:
   ```bash
   vercel --prod
   ```

You'll get a URL like `https://your-project.vercel.app` — that's your
submission link. Re-run the `sample_trap_document.pdf` test against the
live URL itself, not just locally, before submitting.

## Design notes

- **Web search**: DuckDuckGo via `ddgs`, no search API key/billing needed.
- **PDF parsing**: `pypdf` (pure Python) rather than `pdfplumber`, since it
  has no compiled-binary dependencies (no Pillow/pypdfium2), which keeps
  Vercel's Python build more reliable.
- **One claim per request**: the frontend calls `/api/verify` once per
  claim (3 at a time) instead of one giant request for all claims, so each
  serverless invocation stays short and the UI updates progressively
  instead of one long spinner.
- **Claim cap**: capped at 20 claims per document in the frontend, to keep
  runs fast and within free-tier API/search usage.
- Set `ANTHROPIC_MODEL` as an env var if you want to swap models (defaults
  to `claude-sonnet-4-6`).

## If something fails on deploy

- **500 error mentioning `ANTHROPIC_API_KEY`**: you haven't added the env
  var yet, or added it but didn't redeploy afterward.
- **Build fails on a dependency**: check the Vercel build logs; pin exact
  versions in `requirements.txt` if a newer release breaks something.
- **Function timeout**: `vercel.json` already extends `app.py` to 60s; if a
  single claim verification still times out, it's almost always the web
  search step taking long on an unusual query — that's a transient issue,
  not a logic bug.
