import gradio as gr
from pathlib import Path
from datetime import datetime
from components.question_loader import load_questions
from components.session_manager import append_session
from components.scoring_engine import score_answer, aggregate_session_scores
from components.transcription_service import transcribe_audio

BASE = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = BASE / "data" / "questions"

def make_progress_bar(current: int, total: int) -> str:
    if total <= 0:
        pct = 0
    else:
        pct = int((current / total) * 100)
    return f"""
    <div style="width:100%;background:#eee;border-radius:8px;overflow:hidden;">
      <div style="
        width:{pct}%;
        background:#01696f;
        height:10px;
        transition:width 0.3s ease;">
      </div>
    </div>
    <p style="font-size:0.9rem;margin-top:4px;">Progress: {current} / {total}</p>
    """

def compute_late(question_started_at: str, answered_at_dt: datetime) -> bool:
    try:
        if question_started_at:
            started_dt = datetime.fromisoformat(question_started_at.replace("Z", ""))
            delta = answered_at_dt - started_dt
            return delta.total_seconds() > 300  # 5 minutes
    except Exception:
        return False
    return False

def start_session(track: str):
    df = load_questions(track, QUESTIONS_DIR)
    num_questions = len(df)

    if num_questions == 0:
        return (
            "No questions available for this track.",
            "",
            0,
            track,
            [],
            False,
            make_progress_bar(0, 0),
            0,
            "",
        )

    first = df.iloc[0]
    question_text = f"[{first['theme']}/{first['sub_theme']}] {first['question_text']}"
    progress_html = make_progress_bar(1, num_questions)
    started_at = datetime.utcnow().isoformat() + "Z"

    return (
        question_text,
        "",
        0,
        track,
        [],
        False,
        progress_html,
        0,        # attempt_count_state
        started_at,
    )

def next_step(
    track: str,
    question_index: int,
    answers_so_far: list,
    audio_path: str,
    attempt_count: int,
    question_started_at: str,
):
    df = load_questions(track, QUESTIONS_DIR)
    num_questions = len(df)

    if num_questions == 0:
        return (
            "No questions available for this track.",
            "No scoring.",
            question_index,
            answers_so_far,
            True,
            make_progress_bar(0, 0),
            attempt_count,
            question_started_at,
        )

    if question_index < 0:
        question_index = 0
    if question_index >= num_questions:
        question_index = num_questions - 1

    answered_at_dt = datetime.utcnow()
    answered_at = answered_at_dt.isoformat() + "Z"
    late = compute_late(question_started_at, answered_at_dt)

    max_attempts = 3
    attempt_number = attempt_count + 1
    if attempt_number > max_attempts:
        feedback_text = (
            "You have reached the maximum of 3 recordings for this question. "
            "Please move on to the next question."
        )
        progress_html = make_progress_bar(question_index + 1, num_questions)
        return (
            f"[Max attempts reached] {df.iloc[question_index]['question_text']}",
            feedback_text,
            question_index,
            answers_so_far,
            False,
            progress_html,
            attempt_count,
            question_started_at,
        )

    row = df.iloc[question_index]
    question_id = row["id"]
    question_text = row["question_text"]
    theme = row.get("theme", "")
    sub_theme = row.get("sub_theme", "")
    risk_tag = row.get("risk_tag", "")

    # Transcribe audio to text (Whisper)
    transcript = transcribe_audio(audio_path)

    # Score transcript using 5C + risk heuristics
    scores = score_answer(transcript, risk_tag=risk_tag, theme=theme)

    answers_so_far.append(
        {
            "question_id": question_id,
            "question_text": question_text,
            "theme": theme,
            "sub_theme": sub_theme,
            "risk_tag": risk_tag,
            "track": track,
            "question_started_at": question_started_at,
            "answered_at": answered_at,
            "late": late,
            "attempt_number": attempt_number,
            "max_attempts": max_attempts,
            "input_mode": "audio",
            "audio_path": audio_path,
            "transcript": transcript,
            "scores": scores,
        }
    )

    feedback_text = (
        f"Attempt {attempt_number} of {max_attempts}. "
        f"{'Answer was late (>5 minutes).' if late else ''}\n"
        f"Transcript (preview): {transcript[:200]}..."
    )

    next_index = question_index + 1

    if next_index >= num_questions:
        # Session complete
        session_id = f"{track.upper()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        session_scores = aggregate_session_scores(track, answers_so_far)

        session = {
            "session_id": session_id,
            "student_id": "UNKNOWN",  # hook in profile later
            "track": track,
            "country": "Nigeria",
            "university_code": "ALL",
            "started_at": answers_so_far[0]["question_started_at"] if answers_so_far else None,
            "completed_at": answered_at,
            "questions": answers_so_far,
            "overall_scores": session_scores,
            "risk_summary": {},  # can aggregate risk_tags later
        }
        append_session(session)

        progress_html = make_progress_bar(num_questions, num_questions)

        return (
            "Session complete. Thank you – counsellors will review your answers.",
            feedback_text,
            question_index,
            answers_so_far,
            True,
            progress_html,
            attempt_number,
            question_started_at,
        )

    # Prepare next question
    next_row = df.iloc[next_index]
    next_question_display = (
        f"[{next_row['theme']}/{next_row['sub_theme']}] {next_row['question_text']}"
    )
    progress_html = make_progress_bar(next_index + 1, num_questions)

    new_started_at = datetime.utcnow().isoformat() + "Z"
    new_attempt_count = 0

    return (
        next_question_display,
        feedback_text,
        next_index,
        answers_so_far,
        False,
        progress_html,
        new_attempt_count,
        new_started_at,
    )

with gr.Blocks(title="Advisors Academy UKVI Simulator") as demo:
    gr.Markdown(
        """
        # Advisors Academy UKVI Simulator
        
        Nigeria-focused UKVI, Pre-CAS, and Credibility interview practice.
        Audio recording, 3 attempts per question, and 5-minute timing.
        """
    )

    with gr.Row():
        track_input = gr.Radio(
            choices=["ukvi", "pre_cas", "credibility"],
            label="Select track",
            value="ukvi",
        )
        start_button = gr.Button("Start session")

    progress_html = gr.HTML(make_progress_bar(0, 0))
    question_box = gr.Textbox(label="Question", interactive=False)
    feedback_box = gr.Textbox(
        label="Feedback (for last answer)", interactive=False, lines=6
    )
    audio_input = gr.Audio(
        source="microphone",
        type="filepath",
        label="Record your answer (audio)",
    )
    next_button = gr.Button("Submit recording & go to next")

    question_index_state = gr.State(0)
    track_state = gr.State("ukvi")
    answers_state = gr.State([])
    session_complete_state = gr.State(False)
    attempt_count_state = gr.State(0)
    question_started_at_state = gr.State("")

    start_button.click(
        start_session,
        inputs=[track_input],
        outputs=[
            question_box,
            feedback_box,
            question_index_state,
            track_state,
            answers_state,
            session_complete_state,
            progress_html,
            attempt_count_state,
            question_started_at_state,
        ],
    )

    next_button.click(
        next_step,
        inputs=[
            track_state,
            question_index_state,
            answers_state,
            audio_input,
            attempt_count_state,
            question_started_at_state,
        ],
        outputs=[
            question_box,
            feedback_box,
            question_index_state,
            answers_state,
            session_complete_state,
            progress_html,
            attempt_count_state,
            question_started_at_state,
        ],
    )

if __name__ == "__main__":
    demo.launch()
