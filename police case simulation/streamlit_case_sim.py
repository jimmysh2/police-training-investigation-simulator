# streamlit_case_sim.py
# Police Case Simulator — loads separate JSON case files from ./cases/
# Run: streamlit run streamlit_case_sim.py

import streamlit as st
import json
from pathlib import Path

# ---------- Config ----------
CASES_DIR = Path("cases")

def list_case_files():
    """Return list of JSON files in cases dir (sorted)."""
    if not CASES_DIR.exists():
        return []
    return sorted([p for p in CASES_DIR.glob("*.json")])

def load_case_from_path(path: Path):
    """Load and return JSON case, or raise."""
    return json.loads(path.read_text(encoding="utf-8"))

st.set_page_config(page_title="Police Case Simulator", layout="centered")
st.title("Police Case Simulator")

# ---------- List available cases ----------
case_files = list_case_files()
if not case_files:
    st.error("No case files found. Put one or more JSON case files into the ./cases/ folder and reload.")
    st.info("I can provide sample JSONs if you want. Files must have keys: id, title, summary, stages (list).")
    st.stop()

# Build display names
display_names = [f.name for f in case_files]
selected_name = st.sidebar.selectbox("Choose case file", display_names)
selected_path = CASES_DIR / selected_name

# Load selected case
try:
    case = load_case_from_path(selected_path)
except Exception as e:
    st.error(f"Failed to read selected case file: {e}")
    st.stop()

# Basic validation
if not isinstance(case, dict) or "stages" not in case or "title" not in case:
    st.error("Invalid case JSON structure. Required keys: id, title, summary, stages (list).")
    st.stop()

# ---------- Simulator state keys are kept per selected file so switching resets ----------
state_prefix = f"case::{selected_name}::"

def sget(key, default=None):
    return st.session_state.get(state_prefix + key, default)

def sset(key, val):
    st.session_state[state_prefix + key] = val

# Initialize per-case session state defaults
if sget("stage_idx") is None:
    sset("stage_idx", 0)
if sget("score") is None:
    sset("score", 0.0)
if sget("history") is None:
    sset("history", [])
if sget("attempts") is None:
    sset("attempts", {})
if sget("stage_solved") is None:
    sset("stage_solved", False)
if sget("stage_recorded") is None:
    sset("stage_recorded", {})
if sget("last_hint") is None:
    sset("last_hint", "")
if sget("last_submitted_idx") is None:
    sset("last_submitted_idx", None)
if sget("just_submitted") is None:
    sset("just_submitted", False)

# ---------- Page header ----------
st.header(case.get("title", "Untitled Case"))
st.write(case.get("summary", ""))

# ---------- Helper to save changes to session state ----------
def reset_case_state():
    sset("stage_idx", 0)
    sset("score", 0.0)
    sset("history", [])
    sset("attempts", {})
    sset("stage_solved", False)
    sset("stage_recorded", {})
    sset("last_hint", "")
    sset("last_submitted_idx", None)
    sset("just_submitted", False)

# If user switches case file via sidebar, the key prefix changes and state resets naturally.
# But provide a manual reset button:
if st.sidebar.button("Reset this case progress"):
    reset_case_state()
    st.rerun()

# ---------- End-of-case ----------
stage_idx = sget("stage_idx")
stages = case["stages"]
if stage_idx >= len(stages):
    st.success(f"Simulation complete. Score: {sget('score')}/{len(stages)}")
    st.write("Completed stages are shown below.")
    if st.button("Restart Case"):
        reset_case_state()
        st.rerun()
    st.write("---")

# ---------- Show history ----------
history = sget("history")
if history:
    st.subheader("Completed stages (correct answers)")
    for rec in history:
        with st.expander(f"Stage {rec['stage_idx'] + 1} — Completed", expanded=False):
            st.write("**Given info:**")
            st.write(rec["info"])
            st.write("**Final (correct) action:** " + rec["chosen"])
            st.write("Attempts made before success: " + str(rec.get("attempts_count", 1)))
            if rec.get("next_info"):
                st.write("**Next info revealed:** " + rec["next_info"])
            st.write("---")
    st.write("### Continue below to attempt the next stage")
    st.write("")

# ---------- Current stage UI ----------
if stage_idx < len(stages):
    stage = stages[stage_idx]
    st.subheader(f"Stage {stage_idx + 1}")
    st.write(stage.get("info", ""))
    st.write("**Question:** " + stage.get("question", ""))

    # attempts list
    attempts_list = sget("attempts").get(str(stage_idx), [])
    if attempts_list:
        st.write("Previous attempts for this stage:")
        for i, a_idx in enumerate(attempts_list, start=1):
            choice_text = stage["options"][a_idx] if 0 <= a_idx < len(stage["options"]) else "Invalid choice"
            st.write(f"- Attempt {i}: {choice_text}")
        st.write("---")

    # solved branch
    if sget("stage_solved"):
        st.success("Correct. Review the next info below. Click 'Next Stage' when ready to proceed.")
        st.write("**Next info:** " + stage.get("next_info", ""))

        if not sget("stage_recorded").get(str(stage_idx), False):
            attempts_count = len(sget("attempts").get(str(stage_idx), []))
            rec = {
                "stage_idx": stage_idx,
                "info": stage.get("info", ""),
                "question": stage.get("question", ""),
                "chosen": stage["options"][stage.get("correct")],
                "chosen_idx": stage.get("correct"),
                "correct": True,
                "attempts_count": attempts_count,
                "next_info": stage.get("next_info", "")
            }
            # append to history
            h = sget("history")
            h.append(rec)
            sset("history", h)
            # mark recorded
            sr = sget("stage_recorded")
            sr[str(stage_idx)] = True
            sset("stage_recorded", sr)

        if st.button("Next Stage"):
            sset("stage_idx", stage_idx + 1)
            sset("stage_solved", False)
            sset("last_hint", "")
            sset("last_submitted_idx", None)
            sset("just_submitted", False)
            st.rerun()
    else:
        # show hint if any
        if sget("last_hint"):
            st.info("Hint: " + sget("last_hint"))

        # submission form
        with st.form(key=f"form_stage_{stage_idx}"):
            choice = st.radio("Choose next step", stage.get("options", []), index=0, key=f"choice_{stage_idx}")
            submitted = st.form_submit_button("Submit Answer")

        if submitted:
            try:
                selected_idx = stage["options"].index(choice)
            except Exception:
                selected_idx = -1

            # record attempt
            at = sget("attempts")
            at.setdefault(str(stage_idx), []).append(selected_idx)
            sset("attempts", at)
            sset("last_submitted_idx", selected_idx)
            sset("just_submitted", True)

            if selected_idx == stage.get("correct"):
                sset("score", sget("score") + 1.0)
                sset("stage_solved", True)
                # clear hint
                sset("last_hint", "")
                attempts_count = len(sget("attempts").get(str(stage_idx), []))
                st.success(f"Correct. Stage solved in {attempts_count} attempt(s). Review next info and click 'Next Stage' to continue.")
                st.write("**Next info:** " + stage.get("next_info", ""))
                st.rerun()
            else:
                # incorrect -> set hint, do not rerun here (form already caused a re-run)
                hint = stage.get("feedback_wrong", "Incorrect. Try again.")
                sset("last_hint", hint)
                st.error("Incorrect. Try again.")
                st.info("Hint: " + hint)

# ---------- Sidebar: progress -->
st.sidebar.header("Progress")
st.sidebar.write(f"Case file: {selected_name}")
st.sidebar.write(f"Case title: {case.get('title', '')}")
st.sidebar.write(f"Score: {sget('score')} / {len(stages)}")
st.sidebar.write(f"Stage: {min(sget('stage_idx'), len(stages))} / {len(stages)}")
st.sidebar.write("---")
st.sidebar.write("Instructions:\n- Put case JSON files into ./cases/ folder.\n- Select a case from the sidebar. Each case's progress is kept separately in session.\n- Stage advances only after correct answer AND clicking Next Stage.")
