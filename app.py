import datetime as dt
import streamlit as st
from agent import MeetingPrepAgent
import seed_data


st.set_page_config(page_title="Meeting Prep Agent (Hindsight)", page_icon="🧠", layout="wide")


@st.cache_resource
def get_agent():
    return MeetingPrepAgent()


try:
    agent = get_agent()
except Exception as e:
    st.error(f"Setup problem: {e}. Copy .env.example to .env and add your keys.")
    st.stop()

st.title("🧠 Meeting Prep Agent")
st.caption("An AI chief-of-staff that remembers every meeting, promise and missed follow-up - powered by Hindsight memory.")

with st.sidebar:
    st.header("Demo data")
    if st.button("Load demo history"):
        with st.spinner("Retaining memories in Hindsight..."):
            for m in seed_data.MEETINGS:
                agent.log_meeting(**m)
            for c, item, d in seed_data.FOLLOWUP_DONE:
                agent.complete_followup(c, item, d)
            for p in seed_data.PREFERENCES:
                agent.save_preference(p)
        st.success("Loaded 4 meetings + 3 preferences")
    st.divider()
    st.subheader("Teach my style")
    pref = st.text_input("e.g. 'Always include competitor context'")
    if st.button("Save preference") and pref:
        agent.save_preference(pref)
        st.success("Preference remembered")

tab1, tab2, tab3 = st.tabs(["📋 Prep Brief", "📝 Log Meeting", "✅ Close Follow-up"])

with tab1:
    c1, c2 = st.columns(2)
    contact = c1.text_input("Contact", "Priya Nair")
    purpose = c2.text_input("Meeting purpose", "Negotiate pricing and get CFO intro")
    if st.button("Generate brief", type="primary"):
        with st.spinner("Recalling memories and reflecting..."):
            plain = agent.brief_without_memory(contact, purpose)
            smart, memories, prefs, insight = agent.brief_with_memory(contact, purpose)
        left, right = st.columns(2)
        left.subheader("❌ Without memory")
        left.write(plain)
        right.subheader("✅ With Hindsight memory")
        right.write(smart)
        with st.expander(f"🔎 {len(memories)} memories recalled (proof)"):
            for m in memories:
                st.markdown(f"- {m}")
        with st.expander("⚙️ Preferences applied"):
            for p in prefs:
                st.markdown(f"- {p}")
        with st.expander("💡 Reflect insights"):
            st.write(insight)

with tab2:
    with st.form("log"):
        a, b = st.columns(2)
        who = a.text_input("Contact")
        comp = b.text_input("Company")
        date = st.date_input("Date", dt.date.today())
        summ = st.text_area("What was discussed?")
        mine = st.text_input("What I promised")
        theirs = st.text_input("What they promised")
        opn = st.text_input("Open follow-ups")
        if st.form_submit_button("Save to memory") and who and summ:
            agent.log_meeting(who, comp, str(date), summ, mine, theirs, opn)
            st.success("Meeting retained in Hindsight")

with tab3:
    who2 = st.text_input("Contact ", "Priya Nair")
    item = st.text_input("Follow-up completed", "Sent volume pricing proposal")
    if st.button("Mark done"):
        agent.complete_followup(who2, item, str(dt.date.today()))
        st.success("Recorded - future briefs will stop flagging it")
