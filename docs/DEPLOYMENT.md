# Deployment (Epic 6) - Streamlit Community Cloud (free)

1. Push the project to a **public GitHub repo** (the `.gitignore` keeps `venv/` and `.env` out).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** -> choose your repo, branch `main`, main file `app.py`.
4. Open **Advanced settings -> Secrets** and add:
   ```
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Deploy**. After a few minutes you get a public URL like `https://your-app.streamlit.app`.
6. Paste that URL into **Add Demo Link** on your platform.

## If deployment fails
- "ModuleNotFoundError": a package is missing from `requirements.txt`.
- "No Gemini API key found": the secret name must be exactly `GEMINI_API_KEY`.
- App sleeps after inactivity: normal on the free tier; opening the link wakes it up.
