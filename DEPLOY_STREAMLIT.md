# Deploy "The Awkward Translator" on Streamlit Community Cloud (free, ~10 min)

You need 3 things, all free: a GitHub account, a Streamlit Cloud account, and a Gemini API key.

---

## Step 0 — Get a free Gemini key (1 min)
1. Go to https://aistudio.google.com/apikey  (sign in with Google)
2. Click "Create API key" → copy the key (starts with `AIza...`)
3. Keep it somewhere safe for Step 3. (No credit card needed.)

---

## Step 1 — Put the files on GitHub (web, no commands)
1. Go to https://github.com → sign in → click "+" (top right) → "New repository".
2. Name it (e.g. `awkward-translator`), keep **Public**, click "Create repository".
3. On the new repo page, click "uploading an existing file".
4. Drag in these 2 files (the only ones you need):
   - `app.py`
   - `requirements.txt`
   (`.gitignore` is optional but nice. Do NOT upload any secrets file.)
5. Click "Commit changes".

> Your API key is NOT in these files — it goes in Streamlit's Secrets (Step 3),
> so a public repo is safe.

---

## Step 2 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io → sign in with GitHub → "Authorize".
2. Click "Create app" / "New app" → "Deploy a public app from GitHub".
3. Fill in:
   - Repository: `your-username/awkward-translator`
   - Branch: `main`
   - Main file path: `app.py`
4. Click "Deploy". It builds for ~1–2 min (installs requirements). It may show
   "demo mode" at first — that's expected until you add the key in Step 3.

---

## Step 3 — Add your key (Secrets)
1. On your app page, click the "⋮" (or "Manage app") → "Settings" → "Secrets".
2. Paste this (use YOUR key), then Save:

   ```toml
   FREE_PROVIDER  = "gemini"
   GEMINI_API_KEY = "AIza...your_key_here"

   # optional:
   # COFFEE_URL   = "https://buymeacoffee.com/your_id"
   # FEEDBACK_URL = "https://forms.gle/your_form"
   ```
3. The app reboots automatically. Done — share your app URL!

---

## Verify it works
- Pick a situation → type something → "✿ write it for me".
- Under the button you should see "✦ free — 5 uses left today" (not "demo mode").
- If it still says demo mode: re-check the Secrets are saved and the key is correct.

## Good to know
- Free tier: app may "sleep" after long inactivity; the first visit then takes
  ~30s to wake, after that it's fast.
- The shared key is used by ALL visitors and has a daily cap (~1,000 generations
  across everyone). When a visitor uses their 5 free/day, they're offered to add
  their own key. This is plenty to launch and grow.
- To update the app later: just edit the file on GitHub → Streamlit redeploys.
