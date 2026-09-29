"""Meeting Prep Agent - core logic.

Hindsight memory is used in three ways:
  retain  -> every meeting, promise, follow-up and preference is stored
  recall  -> pulls everything known about one contact + the user's style prefs
  reflect -> synthesises patterns ("Priya always pushes back on price")
"""
import os
import re
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "meeting-prep-agent")
MODELS = [os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"), "qwen/qwen3-32b", "llama-3.3-70b-versatile"]

SYSTEM = (
    "You are an executive meeting-prep assistant. Write a crisp pre-meeting brief. "
    "Only state facts that appear in the provided memory; never invent history. "
    "If no memory is provided, say clearly that you have no history with this contact."
)


def _texts(resp):
    """Extract text from a Hindsight recall response defensively."""
    items = getattr(resp, "results", resp) or []
    return [getattr(r, "text", None) or str(r) for r in items]


class MeetingPrepAgent:
    def __init__(self):
        url = os.getenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
        key = os.getenv("HINDSIGHT_API_KEY")
        self.memory = Hindsight(base_url=url, api_key=key) if key else Hindsight(base_url=url)
        self.llm = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.bank = BANK_ID

    # ---------- LLM with fallback (handles model / function-call errors) ----------
    def _chat(self, user_prompt: str) -> str:
        last_err = None
        for model in dict.fromkeys(MODELS):
            try:
                out = self.llm.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": SYSTEM},
                              {"role": "user", "content": user_prompt}],
                    temperature=0.3,
                )
                text = out.choices[0].message.content or ""
                return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            except Exception as e:  # try next model
                last_err = e
        return f"LLM error: {last_err}"

    # ---------- RETAIN ----------
    def log_meeting(self, contact, company, date, summary, i_promised="", they_promised="", open_items=""):
        parts = [f"Meeting with {contact} ({company}) on {date}.", f"Summary: {summary}"]
        if i_promised:
            parts.append(f"I promised {contact}: {i_promised}")
        if they_promised:
            parts.append(f"{contact} promised me: {they_promised}")
        if open_items:
            parts.append(f"Open follow-ups after this meeting: {open_items}")
        self.memory.retain(
            bank_id=self.bank,
            content="\n".join(parts),
            context=f"Meeting notes with {contact}",
            timestamp=f"{date}T10:00:00Z",
        )

    def complete_followup(self, contact, item, date):
        self.memory.retain(
            bank_id=self.bank,
            content=f"Follow-up completed for {contact} on {date}: {item}",
            context=f"Follow-up status for {contact}",
            timestamp=f"{date}T10:00:00Z",
        )

    def save_preference(self, text):
        self.memory.retain(
            bank_id=self.bank,
            content=f"My meeting-preparation preference: {text}",
            context="User's meeting preparation style and preferences",
        )

    # ---------- RECALL ----------
    def recall_contact(self, contact):
        return _texts(self.memory.recall(
            bank_id=self.bank,
            query=f"Past meetings with {contact}: topics discussed, promises made by either side, "
                  f"missed or open follow-ups, concerns and objections",
        ))

    def recall_preferences(self):
        return _texts(self.memory.recall(
            bank_id=self.bank, query="My meeting preparation style and preferences"))

    # ---------- REFLECT ----------
    def insights(self, contact):
        try:
            r = self.memory.reflect(
                bank_id=self.bank,
                query=f"What patterns and risks should I keep in mind when meeting {contact}?")
            return getattr(r, "text", str(r))
        except Exception as e:
            return f"(reflect unavailable: {e})"

    # ---------- BRIEFS ----------
    def brief_without_memory(self, contact, purpose):
        return self._chat(
            f"Prepare me for a meeting with {contact}. Purpose: {purpose}.\n"
            "Format: Objective, Talking points, Questions to ask.")

    def brief_with_memory(self, contact, purpose):
        memories = self.recall_contact(contact)
        prefs = self.recall_preferences()
        insight = self.insights(contact)
        prompt = (
            f"Prepare me for a meeting with {contact}. Purpose: {purpose}.\n\n"
            f"MEMORY - past interactions:\n" + "\n".join(f"- {m}" for m in memories) +
            f"\n\nMEMORY - my preferences (follow them strictly):\n" + "\n".join(f"- {p}" for p in prefs) +
            f"\n\nMEMORY - synthesised insights:\n{insight}\n\n"
            "Format: 1) Relationship snapshot 2) Promises I made 3) Promises they made "
            "4) MISSED / OVERDUE follow-ups (flag clearly; skip anything marked completed) "
            "5) Suggested talking points 6) Risks. Be concise."
        )
        return self._chat(prompt), memories, prefs, insight
