# 🧠 Meeting Prep Agent (HackwithHyderabad 3.0)

An AI agent that remembers every past meeting with each contact - what was discussed, what was promised, which follow-ups were missed - and learns *your* prep style. Built on **Hindsight** memory.

## Why memory is the star
| Hindsight op | How it is used |
|---|---|
| `retain` | Stores each meeting, promise, completed follow-up and style preference (with real meeting dates) |
| `recall` | Pulls everything about one contact + your preferences before each brief |
| `reflect` | Synthesises patterns/risks ("pricing is the recurring blocker") |

The UI shows **Without memory vs With memory** side by side, plus the exact memories recalled.

## Run
```bash
pip install -r requirements.txt
cp .env.example .env        # add HINDSIGHT_API_KEY and GROQ_API_KEY
streamlit run app.py
```
Click **Load demo history** in the sidebar, then generate a brief for `Priya Nair`.

## Demo story (60 sec)
1. Brief for Priya with no history -> generic.
2. Load demo history -> brief now flags the overdue volume pricing, the CFO intro and Datadog's 20% offer.
3. Save preference "always start with a one-line opener" -> brief style changes.
4. Mark pricing follow-up done -> next brief stops flagging it.

## Stack
Python, Streamlit, Hindsight (`hindsight-client`), Groq (`openai/gpt-oss-120b`, with automatic model fallback).
