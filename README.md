# The Fact-Check Agent

A web app that reads a PDF, extracts specific checkable claims (statistics,
dates, financial and technical figures), searches the live web for each
one, and flags it as **Verified**, **Inaccurate**, or **False** — with the
correct fact attached.

Built for the CogCulture Product Management Trainee assessment (Part 2).

## How it works

1. **Extract** — `pdf_utils.py` pulls raw text out of the uploaded PDF with `pdfplumber`.
2. **Identify claims** — `claim_extractor.py` sends the text to Claude with a prompt
   that pulls out only specific, checkable claims (ignoring vague marketing fluff)
   and returns them as structured JSON.
3. **Verify** — `web_verifier.py` runs a live DuckDuckGo search for each claim
   (no search API key needed) and sends the claim + search snippets to Claude,
   which returns a verdict, the corrected fact, and a confidence level.
4. **Report** — `app.py` (Streamlit) renders everything as a scorecard plus a
   claim-by-claim breakdown, and lets you download the full report as JSON.

## Project structure

```
.
├── app.py                     # Streamlit UI
├── pdf_utils.py                # PDF text extraction
├── claim_extractor.py          # Claim extraction via Claude
├── web_verifier.py             # Live search + verdict via Claude
├── make_sample_trap_pdf.py     # Generates a test PDF with planted false/outdated stats
├── sample_trap_document.pdf    # Pre-built test PDF (run the app on this first)
├── requirements.txt
├── .env.example
└── .gitignore
```

## 1. Run it locally first (do this before deploying)

```bash
git clone <your-repo-url>
cd factcheck-agent
python -m venv venv && source venv/bin/activate     # optional but recommended
pip install -r requirements.txt

cp .env.example .env
# open .env and paste your Anthropic API key

streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`), enter
your API key in the sidebar if it isn't picked up from `.env`, and upload
`sample_trap_document.pdf` to do a first end-to-end test. That file has
intentionally planted false and outdated claims (e.g. an "Eiffel Tower is
500 meters tall" line, a wrong founding date for Python) mixed with true
ones, so you can confirm the agent actually catches them before you submit.

Run `python make_sample_trap_pdf.py` if you want to regenerate or edit that
test file.

## 2. Deploy it (mandatory for submission)

The easiest free option is **Streamlit Community Cloud**. Vercel/Render also
work if you'd rather use those — same repo, just follow their Python/Streamlit
deploy docs instead of steps 3-6 below.

1. **Push this folder to a new GitHub repo** (public or private — if private,
   make sure to add the evaluator as a collaborator).
   ```bash
   git init
   git add .
   git commit -m "Fact-Check Agent"
   git branch -M main
   git remote add origin <your-new-repo-url>
   git push -u origin main
   ```
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select your repo, branch `main`, and set the main file
   path to `app.py`.
4. Before clicking deploy, open **Advanced settings → Secrets** and add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-real-key"
   ```
5. Click **Deploy**. The first build takes 2-5 minutes.
6. Once it's live, open the app URL and re-run the `sample_trap_document.pdf`
   test on the deployed version too — this is exactly what an evaluator will do.

You'll end up with a URL like `https://your-app-name.streamlit.app` — that's
the link to put in your submission.

## 3. Submission checklist

- [ ] Deployed app URL (tested with `sample_trap_document.pdf` on the live link, not just locally)
- [ ] Public (or shared) GitHub repo link
- [ ] 30-second screen recording showing: upload PDF → claims extracted → verdicts shown

## Notes on design choices

- **Web search**: uses DuckDuckGo via the `ddgs` package, which needs no API
  key or billing setup — one less moving part for a take-home assessment.
  If you'd rather use Tavily/Serper/Bing for higher-quality results, swap the
  `search_web()` function in `web_verifier.py`; everything else stays the same.
- **LLM**: uses the Anthropic API for both claim extraction and verdict
  reasoning. Model is selectable in the sidebar (`claude-sonnet-4-6` by default —
  good accuracy/cost balance for this task).
- **Claim cap**: the sidebar slider limits how many claims get verified per
  run, since each claim costs one search + one LLM call. Useful for staying
  within free-tier credits while testing.
- **Failure mode**: if a PDF is scanned/image-only with no extractable text,
  the app tells you rather than silently returning nothing — OCR isn't wired
  in for this version but could be added with `pytesseract`.

## Known limitation

Verdicts are only as good as what's findable via web search snippets in the
few seconds the app waits on each claim. For very recent or niche claims
with thin web coverage, the agent will say so via a "low confidence" or
"No reliable evidence found" result rather than guessing.

