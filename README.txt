
Police Case Simulator Demo
-------------------------
Files:
- case_simulator_console.py: Console interactive simulator (use python to run).
- streamlit_case_sim.py: Streamlit app (run with `streamlit run streamlit_case_sim.py`).
- case_demo_001.json: Sample case in JSON format (edit to add real cases later).

How it works:
- Each case has multiple 'stages'. At each stage the trainee is shown info and asked to choose next step.
- Correct choices increase score; wrong choices show feedback and allow a retry.
- You can author new cases by creating JSON files similar to the sample case.

Next steps I can help with:
- Add persistence (user accounts, progress saving).
- Add admin UI to upload/author cases.
- Expand scoring, add time limits and resources constraints.
- Integrate CDR/CDR-request templates and checklists into stages.
