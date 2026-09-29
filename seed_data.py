"""Loads realistic synthetic history so the demo shows memory from day one.
Run:  python seed_data.py
"""
from agent import MeetingPrepAgent

MEETINGS = [
    dict(contact="Priya Nair", company="Finovate Payments", date="2026-07-08",
         summary="Discovery call. Priya (VP Engineering) struggles with 4-hour incident triage across 3 monitoring tools. "
                 "Budget owner is CFO Arjun Rao. Currently evaluating Datadog as well.",
         i_promised="Send a SOC 2 report and a 2-page ROI summary by July 12",
         they_promised="Share current on-call rotation data by July 15",
         open_items="SOC 2 report, ROI summary, on-call data"),
    dict(contact="Priya Nair", company="Finovate Payments", date="2026-07-29",
         summary="Demo to Priya and 2 SREs. Loved alert correlation. Raised concern that pricing per seat is too high "
                 "for a 120-engineer org. Asked about SSO via Okta.",
         i_promised="Come back with a volume-based pricing option and Okta SSO documentation by Aug 5",
         they_promised="Intro me to CFO Arjun Rao",
         open_items="Volume pricing, Okta SSO docs, intro to CFO"),
    dict(contact="Priya Nair", company="Finovate Payments", date="2026-08-26",
         summary="Priya said the intro to the CFO is delayed because of quarter-end. She is frustrated I never sent the "
                 "volume pricing. Datadog offered her a 20% discount. Sensitive: she dislikes long slide decks.",
         i_promised="Send volume pricing proposal by Aug 30",
         they_promised="Book CFO meeting in September",
         open_items="Volume pricing (overdue), Okta SSO docs (overdue), CFO meeting"),
    dict(contact="Rahul Mehta", company="Zenith Retail", date="2026-09-02",
         summary="Intro call. Rahul (Head of Support) wants to cut ticket resolution time. Has a 15-person team. "
                 "Prefers Slack over email.",
         i_promised="Share 2 customer case studies from retail",
         they_promised="Send sample ticket export",
         open_items="Case studies, ticket export"),
]

FOLLOWUP_DONE = [
    ("Priya Nair", "SOC 2 report and ROI summary sent", "2026-07-11"),
]

PREFERENCES = [
    "Keep briefs under 200 words and lead with overdue follow-ups.",
    "I prefer bullet points, no long paragraphs.",
    "Always end the brief with one suggested opening line for the meeting.",
]

if __name__ == "__main__":
    agent = MeetingPrepAgent()
    for m in MEETINGS:
        agent.log_meeting(**m)
        print("retained meeting:", m["contact"], m["date"])
    for c, item, d in FOLLOWUP_DONE:
        agent.complete_followup(c, item, d)
    for p in PREFERENCES:
        agent.save_preference(p)
    print("Seeding complete.")
