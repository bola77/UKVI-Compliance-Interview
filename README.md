#  UKVI Credibility Interview

Hybrid Gradio + Streamlit app for UKVI, Pre-CAS, and Credibility interview
training, starting with Nigeria-focused question banks.

## Structure

- `gradio_app/`: Mock interview simulator (Gradio).
- `streamlit_app/`: Dashboards and counsellor tools (Streamlit).
- `data/questions/`: CSV question banks for UKVI, Pre-CAS, and Credibility.
- `data/session_exports/`: JSON session exports for dashboards.

## Getting started

```bash
pip install -r requirements.txt

# Run simulator
python gradio_app/app.py

# Run dashboards
streamlit run streamlit_app/app.py
```

Update `data/questions/*.csv` as you expand to other countries and universities.
