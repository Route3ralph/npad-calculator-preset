# NovetraSys NPAD Calculator (with Presets)

This Streamlit app compares PPO vs NPAD economics and includes preset scenarios:
- Hospital CFO
- TPA
- Stop-Loss
- Vinny Win

## Run locally
```
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud
1) Push `app.py` and `requirements.txt` to a public GitHub repo.
2) Go to https://streamlit.io → Deploy an app → select your repo → choose `app.py`.
3) Share the URL (mobile-ready).
