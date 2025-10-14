# Developer setup

1. Install Python 3.11 or higher.
2. Create a virtual environment and run `pip install -r requirements.txt`.
3. Run `python -m pytest -q`.
4. Run `uvicorn app.main:app --reload` from the repository root.
5. In another terminal run `streamlit run dashboard/app.py`.

The project uses a local SQLite database. Delete it only when you intentionally want to reset the demo. Configuration uses environment variables and optional `.env`; never commit `.env`.
