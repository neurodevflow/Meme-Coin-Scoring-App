import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import numpy as np

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Meme Coin Launch Studio",
    page_icon="💊",
    layout="wide"
)

IDEAS_FILE = "ideas.json"


# ---------- PERSISTENCE HELPERS ----------
def load_ideas():
    if not os.path.exists(IDEAS_FILE):
        return []
    try:
        with open(IDEAS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_ideas(ideas):
    with open(IDEAS_FILE, "w", encoding="utf-8") as f:
        json.dump(ideas, f, ensure_ascii=False, indent=2)


# ---------- SCORING / RATING ----------
def rate_score(score: int) -> str:
    if score >= 32:
        return "S‑Tier"
    elif score >= 28:
        return "A‑Tier"
    elif score >= 22:
        return "B‑Tier"
    else:
        return "Weak"


def tier_description(tier: str) -> str:
    if tier == "S‑Tier":
        return "Launch immediately, double down on narrative and distribution."
    elif tier == "A‑Tier":
        return "Strong – refine weak spots, then launch."
    elif tier == "B‑Tier":
        return "Mid – iterate hard on meme and social energy."
    else:
        return "Do not launch yet – rework the core concept."


def compute_meme_readiness(scores: dict) -> int:
    # scores is dict of 8 criteria (0–5)
    mf = scores["Concept Clarity"] + scores["Remixability"] + scores["Cultural Bandwidth"]
    se = scores["Reply‑Bait Potential"] + scores["Conflict / Tension"] + scores["Status Signaling"]
    aa = scores["Narrative Hook"] + scores["Character / Symbol Strength"]

    # Normalize each bucket to 0–1
    mf_norm = mf / 15
    se_norm = se / 15
    aa_norm = aa / 10

    readiness = 0.4 * se_norm + 0.3 * mf_norm + 0.3 * aa_norm
    return int(round(readiness * 100))


# ---------- HEURISTIC AUTO‑SCORING ----------
def heuristic_auto_score(name: str, narrative: str) -> dict:
    """
    Rough, rule‑based scoring to reduce your own bias.
    It looks at length, presence of conflict words, etc.
    Not AI, but a consistent heuristic.
    """

    text = (name + " " + narrative).lower()
    length = len(narrative)

    def clamp(x, lo=0, hi=5):
        return max(lo, min(hi, x))

    # Concept clarity: short, focused narratives get higher score
    if length < 60:
        concept_clarity = 2
    elif length < 250:
        concept_clarity = 4
    else:
        concept_clarity = 3
    if any(k in text for k in ["coin for", "this coin is for", "official coin of"]):
        concept_clarity += 1

    # Remixability: presence of archetypes / universal roles
    remix_words = ["dev", "developer", "applicant", "visa", "whale", "union",
                   "boss", "founder", "worker", "student", "rejected", "hiring"]
    remixability = 2 + sum(w in text for w in remix_words)
    remixability = clamp(remixability)

    # Cultural bandwidth: global pains and simple concepts
    global_pain_words = ["visa", "job", "salary", "boss", "tax", "rent", "queue",
                         "rejected", "ghosted", "work", "burnout"]
    cb_score = 2 + sum(w in text for w in global_pain_words)
    cultural_bandwidth = clamp(cb_score)

    # Reply‑bait: confession / story prompts
    reply_words = ["story", "confession", "share", "reply", "tell", "chat"]
    reply_bait = 2 + sum(w in text for w in reply_words)
    reply_bait = clamp(reply_bait)

    # Conflict / tension: enemies and versus framing
    conflict_words = ["boss", "founder", "hr", "ats", "embassy", "government",
                      "landlord", "system", "rejected", "ghosted", "underpaid"]
    conflict_tension = 1 + sum(w in text for w in conflict_words)
    conflict_tension = clamp(conflict_tension)

    # Status signaling: identity groups
    status_words = ["dev", "developer", "applicant", "founder", "immigrant",
                    "worker", "survivor", "union", "community"]
    status_signaling = 2 + sum(w in text for w in status_words)
    status_signaling = clamp(status_signaling)

    # Narrative hook: if we can see a clear headline
    hook_words = ["finally", "official", "revolution", "union", "survivor",
                  "economy", "queue", "launch", "token"]
    narrative_hook = 2 + sum(w in text for w in hook_words)
    narrative_hook = clamp(narrative_hook)

    # Character / symbol strength: obvious mascots
    symbol_words = ["turtle", "whale", "ghost", "cop", "battery", "butt",
                    "applicant", "dev", "robot", "queue"]
    character_strength = 2 + sum(w in text for w in symbol_words)
    character_strength = clamp(character_strength)

    scores = {
        "Concept Clarity": clamp(concept_clarity),
        "Remixability": remixability,
        "Cultural Bandwidth": cultural_bandwidth,
        "Reply‑Bait Potential": reply_bait,
        "Conflict / Tension": conflict_tension,
        "Status Signaling": status_signaling,
        "Narrative Hook": narrative_hook,
        "Character / Symbol Strength": character_strength,
    }
    return scores


# ---------- DESCRIPTION GENERATOR ----------
def generate_pumpfun_descriptions(name: str, ticker: str, narrative: str):
    base = narrative.strip()
    if not base:
        base = f"{name} is a degen little experiment."

    short = f"{name} ({ticker}) – {base[:160]}"

    funny = (
        f"{name} ({ticker})\n\n"
        f"{base}\n\n"
        "You probably won’t get rich, but at least you’ll finally have a coin that understands your pain."
    )

    emotional = (
        f"{name} ({ticker}) is for everyone who feels this story in their bones.\n\n"
        f"{base}\n\n"
        "If this sounds like your life, you’re already early."
    )

    aggressive = (
        f"{name} ({ticker}) exists because nobody else fixed this.\n\n"
        f"{base}\n\n"
        "If you’re tired of being ignored, underpaid, or ghosted – buy and make noise."
    )

    long = (
        f"{name} ({ticker})\n\n"
        f"{base}\n\n"
        "This isn’t financial advice. This is emotional damage tokenized.\n"
        "Reply with your story in the thread and join the chaos."
    )

    return {
        "Short": short,
        "Funny": funny,
        "Emotional": emotional,
        "Aggressive": aggressive,
        "Long": long,
    }


# ---------- MASCOT SUGGESTION GENERATOR ----------
def generate_mascot_suggestions(name: str, narrative: str):
    text = (name + " " + narrative).lower()
    ideas = []

    if any(word in text for word in ["applicant", "reject", "cv", "job", "ats"]):
        ideas.append("A small character holding a crumpled CV with a big RED 'REJECTED' stamp on their forehead.")
        ideas.append("A walking email envelope with sad eyes and a giant 'We went with another candidate' preview line.")
    if any(word in text for word in ["dev", "developer", "code", "bug", "feature", "sprint"]):
        ideas.append("Exhausted developer with red eyes, hoodie, laptop, and a pizza slice shaped like a middle finger.")
        ideas.append("Pixel‑art dev sitting on a stack of bug reports with coffee IV drip.")
    if any(word in text for word in ["visa", "queue", "embassy", "passport"]):
        ideas.append("A long snake‑like queue of tiny characters, one waving a passport and looking exhausted.")
        ideas.append("A passport character stuck inside an hourglass with sand running out.")
    if any(word in text for word in ["burnout", "tired", "exhausted", "caffeine", "coffee"]):
        ideas.append("Human‑shaped battery at 3% charge, plugged into a coffee mug like a power adapter.")
    if any(word in text for word in ["butt", "ass"]):
        ideas.append("A cartoon butt with a tiny bandage and a 'Work Broke Me' tattoo.")
    if not ideas:
        ideas.append("Pick a simple archetype: worker, applicant, ghost, cop, turtle, whale – then exaggerate it hard.")
        ideas.append("Design a mascot that could be drawn in 4–5 simple shapes so people can easily remix it.")

    emojis = []
    if "visa" in text or "queue" in text:
        emojis = ["🛂", "🧳", "⏳"]
    elif "dev" in text:
        emojis = ["👨‍💻", "👩‍💻", "☕"]
    elif "reject" in text:
        emojis = ["📩", "❌", "💔"]
    elif "burnout" in text:
        emojis = ["🔋", "😵‍💫", "☕"]
    else:
        emojis = ["🧠", "🔥", "🎭"]

    return ideas, emojis


# ---------- SESSION STATE ----------
if "ideas" not in st.session_state:
    st.session_state.ideas = load_ideas()


def find_idea_by_name(name: str):
    for idea in st.session_state.ideas:
        if idea["name"].strip().lower() == name.strip().lower():
            return idea
    return None


# ---------- LAYOUT: TABS ----------
st.title("💊 Meme Coin Launch Studio")
st.caption("Score, store, compare, and prepare degen‑ready meme coins with a 40‑point model + launch tools.")

tabs = st.tabs([
    "Score Idea",
    "Idea Vault",
    "Comparison Dashboard",
    "Launch Checklist",
    "Generators",
    "Settings",
])

# ---------- TAB 1: SCORE IDEA ----------
with tabs[0]:
    st.header("Score a meme coin idea")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Idea details")

        idea_name = st.text_input("Idea name", placeholder="e.g., Rejected Applicant Coin")
        ticker = st.text_input("Ticker", placeholder="e.g., $REKTAPP")
        narrative = st.text_area(
            "Core narrative (1–3 paragraphs)",
            placeholder="Describe the story, pain, or joke behind this coin.",
            height=200,
        )

        auto_mode = st.checkbox("Auto‑score this idea (reduce manual bias)", value=True)
        st.caption("You can still adjust scores manually if you want fine‑tuning.")

    with col_right:
        st.subheader("Optional: load existing idea")
        all_names = [idea["name"] for idea in st.session_state.ideas]
        if all_names:
            selected_existing = st.selectbox("Load idea from vault", ["None"] + all_names)
            if selected_existing != "None":
                existing = find_idea_by_name(selected_existing)
                if existing:
                    if st.button("Load selected idea here"):
                        idea_name = existing["name"]
                        ticker = existing.get("ticker", "")
                        narrative = existing.get("narrative", "")
                        st.experimental_rerun()

    st.markdown("---")

    # Auto or manual scores
    if auto_mode:
        scores = heuristic_auto_score(idea_name, narrative)
    else:
        scores = {
            "Concept Clarity": 3,
            "Remixability": 3,
            "Cultural Bandwidth": 3,
            "Reply‑Bait Potential": 3,
            "Conflict / Tension": 3,
            "Status Signaling": 3,
            "Narrative Hook": 3,
            "Character / Symbol Strength": 3,
        }

    # Show sliders with prefilled scores (for optional tweak)
    st.subheader("Scoring (0–5 per criterion)")
    st.caption("Adjust only if you strongly disagree with the auto‑score.")

    cols = st.columns(2)
    with cols[0]:
        scores["Concept Clarity"] = st.slider(
            "Concept Clarity – Understandable in 3 seconds?",
            0, 5, scores["Concept Clarity"],
        )
        scores["Remixability"] = st.slider(
            "Remixability – Easy to create variations and running jokes?",
            0, 5, scores["Remixability"],
        )
        scores["Cultural Bandwidth"] = st.slider(
            "Cultural Bandwidth – Works across countries and cultures?",
            0, 5, scores["Cultural Bandwidth"],
        )
        scores["Reply‑Bait Potential"] = st.slider(
            "Reply‑Bait Potential – Naturally invites replies, stories, cope?",
            0, 5, scores["Reply‑Bait Potential"],
        )
    with cols[1]:
        scores["Conflict / Tension"] = st.slider(
            "Conflict / Tension – Clear ‘versus’ dynamic?",
            0, 5, scores["Conflict / Tension"],
        )
        scores["Status Signaling"] = st.slider(
            "Status Signaling – Says something about the holder?",
            0, 5, scores["Status Signaling"],
        )
        scores["Narrative Hook"] = st.slider(
            "Narrative Hook – Strong one‑liner potential?",
            0, 5, scores["Narrative Hook"],
        )
        scores["Character / Symbol Strength"] = st.slider(
            "Character / Symbol Strength – Strong icon, mascot, or symbol?",
            0, 5, scores["Character / Symbol Strength"],
        )

    total_score = sum(scores.values())
    tier = rate_score(total_score)
    tier_text = tier_description(tier)
    readiness = compute_meme_readiness(scores)

    st.markdown("---")
    st.subheader("Results")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total score", f"{total_score} / 40")
    with col_b:
        st.metric("Tier", tier)
    with col_c:
        st.metric("Meme‑readiness", f"{readiness} / 100")

    st.write(tier_text)

    with st.expander("See detailed breakdown"):
        for k, v in scores.items():
            st.write(f"- **{k}:** {v} / 5")

    # Suggestions
    st.subheader("Suggestions based on weak dimensions")
    weak_dims = [k for k, v in scores.items() if v <= 2]
    if not weak_dims:
        st.write("This idea looks structurally solid. Focus on launch timing, distribution, and execution.")
    else:
        for dim in weak_dims:
            if dim == "Concept Clarity":
                st.write("- **Concept Clarity:** Reduce your narrative to one brutal, obvious sentence anyone can repeat.")
            elif dim == "Remixability":
                st.write("- **Remixability:** Design 5+ meme formats, screenshots, or rituals people can reuse easily.")
            elif dim == "Cultural Bandwidth":
                st.write("- **Cultural Bandwidth:** Swap niche references for universal pains (money, work, rejection, bureaucracy).")
            elif dim == "Reply‑Bait Potential":
                st.write("- **Reply‑Bait Potential:** Add confession prompts, screenshot prompts, or pain‑sharing prompts to the story.")
            elif dim == "Conflict / Tension":
                st.write("- **Conflict / Tension:** Introduce a clear villain: boss, system, whale, embassy, landlord, etc.")
            elif dim == "Status Signaling":
                st.write("- **Status Signaling:** Make holding the coin signal identity (dev, applicant, survivor, degen, etc.).")
            elif dim == "Narrative Hook":
                st.write("- **Narrative Hook:** Write 5 fake headlines until one feels viral and punchy.")
            elif dim == "Character / Symbol Strength":
                st.write("- **Character / Symbol Strength:** Attach a simple, iconic mascot people can draw, screenshot, and spam.")

    st.markdown("---")
    st.subheader("Save this idea to your vault")

    notes = st.text_area(
        "Notes (optional)",
        placeholder="Launch thoughts, variations to test, influencer angles, etc.",
        height=120,
    )

    if st.button("Save / Update Idea"):
        if not idea_name:
            st.warning("You need at least an idea name to save.")
        else:
            timestamp = datetime.utcnow().isoformat() + "Z"
            new_entry = {
                "name": idea_name,
                "ticker": ticker,
                "narrative": narrative,
                "scores": scores,
                "total_score": total_score,
                "tier": tier,
                "meme_readiness": readiness,
                "notes": notes,
                "timestamp": timestamp,
                "checklist": {},  # will be filled in Launch Checklist tab
            }

            # Update or append
            updated = False
            for i, idea in enumerate(st.session_state.ideas):
                if idea["name"].strip().lower() == idea_name.strip().lower():
                    st.session_state.ideas[i] = {
                        **idea,
                        **new_entry,
                        "checklist": idea.get("checklist", {}),
                    }
                    updated = True
                    break
            if not updated:
                st.session_state.ideas.append(new_entry)

            save_ideas(st.session_state.ideas)
            st.success("Idea saved / updated in vault.")


# ---------- TAB 2: IDEA VAULT ----------
with tabs[1]:
    st.header("Idea vault")

    ideas = st.session_state.ideas
    if not ideas:
        st.info("No ideas saved yet. Use the 'Score Idea' tab to add one.")
    else:
        df = pd.DataFrame([
            {
                "Name": idea["name"],
                "Ticker": idea.get("ticker", ""),
                "Total Score": idea.get("total_score", 0),
                "Tier": idea.get("tier", ""),
                "Meme Readiness": idea.get("meme_readiness", 0),
                "Saved At": idea.get("timestamp", ""),
            }
            for idea in ideas
        ])
        df_sorted = df.sort_values(by="Total Score", ascending=False).reset_index(drop=True)
        st.dataframe(df_sorted, use_container_width=True)

        st.markdown("#### Clone or edit an idea")
        selected_name = st.selectbox("Select idea", df_sorted["Name"].tolist())
        selected_idea = find_idea_by_name(selected_name)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load into Score tab"):
                st.session_state["load_name"] = selected_name
                st.info("Go back to 'Score Idea' tab and use the dropdown to load it.")
            if st.button("Clone idea"):
                if selected_idea:
                    clone = selected_idea.copy()
                    clone["name"] = selected_idea["name"] + " (Clone)"
                    clone["timestamp"] = datetime.utcnow().isoformat() + "Z"
                    st.session_state.ideas.append(clone)
                    save_ideas(st.session_state.ideas)
                    st.success("Idea cloned.")
        with col2:
            if st.button("Delete idea"):
                st.session_state.ideas = [i for i in st.session_state.ideas if i["name"] != selected_name]
                save_ideas(st.session_state.ideas)
                st.success("Idea deleted.")
                st.experimental_rerun()

        st.markdown("#### Edit notes for selected idea")
        if selected_idea:
            current_notes = selected_idea.get("notes", "")
            updated_notes = st.text_area(
                "Notes",
                value=current_notes,
                height=150,
            )
            if st.button("Save notes"):
                for i, idea in enumerate(st.session_state.ideas):
                    if idea["name"] == selected_name:
                        st.session_state.ideas[i]["notes"] = updated_notes
                        break
                save_ideas(st.session_state.ideas)
                st.success("Notes updated.")

        # Download
        csv = df_sorted.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download vault as CSV",
            data=csv,
            file_name="meme_coin_ideas_vault.csv",
            mime="text/csv",
        )


# ---------- TAB 3: COMPARISON DASHBOARD ----------
with tabs[2]:
    st.header("Comparison dashboard")

    ideas = st.session_state.ideas
    if len(ideas) < 2:
        st.info("Save at least two ideas to compare them.")
    else:
        names = [i["name"] for i in ideas]
        selected_names = st.multiselect("Select ideas to compare", names, default=names[:3])

        selected_ideas = [i for i in ideas if i["name"] in selected_names]

        if selected_ideas:
            comp_df = pd.DataFrame([
                {
                    "Name": i["name"],
                    "Total Score": i.get("total_score", 0),
                    "Meme Readiness": i.get("meme_readiness", 0),
                }
                for i in selected_ideas
            ])
            st.subheader("Total score vs meme‑readiness")
            st.bar_chart(comp_df.set_index("Name"))

            # Radar: 8 dimensions
            st.subheader("Criteria breakdown (radar‑style table)")

            crit_names = [
                "Concept Clarity",
                "Remixability",
                "Cultural Bandwidth",
                "Reply‑Bait Potential",
                "Conflict / Tension",
                "Status Signaling",
                "Narrative Hook",
                "Character / Symbol Strength",
            ]

            radar_data = []
            for i in selected_ideas:
                row = {"Name": i["name"]}
                sc = i.get("scores", {})
                for c in crit_names:
                    row[c] = sc.get(c, 0)
                radar_data.append(row)

            radar_df = pd.DataFrame(radar_data)
            st.dataframe(radar_df.set_index("Name"), use_container_width=True)

            st.subheader("Tier distribution")
            all_df = pd.DataFrame([
                {"Name": i["name"], "Tier": i.get("tier", "Unknown")}
                for i in ideas
            ])
            tier_counts = all_df["Tier"].value_counts()
            st.bar_chart(tier_counts)


# ---------- TAB 4: LAUNCH CHECKLIST ----------
with tabs[3]:
    st.header("Launch checklist")

    ideas = st.session_state.ideas
    if not ideas:
        st.info("Save at least one idea first.")
    else:
        name_for_checklist = st.selectbox(
    "Select idea",
    [i["name"] for i in ideas],
    key="checklist_select"
)

        idea = find_idea_by_name(name_for_checklist)

        if idea:
            default_checklist = {
                "Narrative finalized": False,
                "Mascot selected": False,
                "Reply rituals defined": False,
                "First 10 posts drafted": False,
                "Pump.fun description ready": False,
                "Meme templates created": False,
                "Launch timing decided": False,
                "Seeding / influencer plan": False,
                "Pinned post / announcement ready": False,
            }
            cl = idea.get("checklist", {})
            # merge with defaults
            for k, v in default_checklist.items():
                cl.setdefault(k, v)

            st.subheader(f"Checklist for {name_for_checklist}")
            new_cl = {}
            cols = st.columns(2)
            items = list(cl.items())
            half = len(items) // 2 + len(items) % 2

            with cols[0]:
                for k, v in items[:half]:
                    new_cl[k] = st.checkbox(k, value=v)
            with cols[1]:
                for k, v in items[half:]:
                    new_cl[k] = st.checkbox(k, value=v)

            if st.button("Save checklist"):
                for i, obj in enumerate(st.session_state.ideas):
                    if obj["name"] == name_for_checklist:
                        st.session_state.ideas[i]["checklist"] = new_cl
                        break
                save_ideas(st.session_state.ideas)
                st.success("Checklist updated.")


# ---------- TAB 5: GENERATORS ----------
with tabs[4]:
    st.header("Generators")

    ideas = st.session_state.ideas
    col_gen1, col_gen2 = st.columns(2)

    with col_gen1:
        st.subheader("Pump.fun description generator")
        source_idea_name = st.selectbox(
            "Select idea for description",
            ["Custom narrative"] + [i["name"] for i in ideas],
        )

        if source_idea_name == "Custom narrative":
            d_name = st.text_input("Idea name (for description)", "")
            d_ticker = st.text_input("Ticker (for description)", "")
            d_narr = st.text_area("Narrative", "", height=150)
        else:
            idea = find_idea_by_name(source_idea_name)
            d_name = idea["name"]
            d_ticker = idea.get("ticker", "")
            d_narr = idea.get("narrative", "")

        if st.button("Generate descriptions"):
            descs = generate_pumpfun_descriptions(d_name, d_ticker, d_narr)
            for k, v in descs.items():
                st.markdown(f"**{k} version:**")
                st.code(v)

    with col_gen2:
        st.subheader("Mascot suggestion generator")
        source_mascot_name = st.selectbox(
            "Select idea for mascot",
            ["Custom"] + [i["name"] for i in ideas],
        )

        if source_mascot_name == "Custom":
            m_name = st.text_input("Idea name (for mascot)", "")
            m_narr = st.text_area("Narrative (for mascot)", "", height=150)
        else:
            idea = find_idea_by_name(source_mascot_name)
            m_name = idea["name"]
            m_narr = idea.get("narrative", "")

        if st.button("Generate mascot suggestions"):
            concepts, emojis = generate_mascot_suggestions(m_name, m_narr)
            st.markdown("**Concept ideas:**")
            for c in concepts:
                st.write(f"- {c}")
            st.markdown("**Emoji palette ideas:**")
            st.write(" ".join(emojis))


# ---------- TAB 6: SETTINGS ----------
with tabs[5]:
    st.header("Settings")

    st.write("Manage stored data and basic configuration.")

    if st.button("Reset vault (delete all ideas)"):
        st.warning("This will delete all saved ideas and cannot be undone.")
        st.session_state.ideas = []
        save_ideas([])
        st.success("Vault cleared. Restart the app to see it empty.")

    st.write("Ideas are stored locally in `ideas.json` in the same folder as this script.")
