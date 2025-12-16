import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ----- CONFIG -----
st.set_page_config(
    page_title="Meme Coin 40‑Point Scoring Vault",
    page_icon="💊",
    layout="centered"
)

IDEAS_FILE = "ideas.json"


# ----- PERSISTENCE HELPERS -----
def load_ideas():
    if not os.path.exists(IDEAS_FILE):
        return []
    with open(IDEAS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []


def save_ideas(ideas):
    with open(IDEAS_FILE, "w", encoding="utf-8") as f:
        json.dump(ideas, f, ensure_ascii=False, indent=2)


# ----- SCORING LOGIC -----
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


# ----- LOAD EXISTING IDEAS -----
if "ideas" not in st.session_state:
    st.session_state.ideas = load_ideas()

ideas = st.session_state.ideas

# ----- PRELOADED SAMPLE IDEAS -----
sample_ideas = {
    "None (start from scratch)": {
        "name": "",
        "ticker": "",
        "narrative": "",
    },
    "BUTT COIN": {
        "name": "BUTT COIN",
        "ticker": "$BUTT",
        "narrative": (
            "I need a new Butt.\n\n"
            "Sure, you might not gain much from buying this—but hey, I just scored a "
            "brand-new butt! And you? You get the warm, fuzzy feeling of helping a "
            "fellow human upgrade their rear end. Curious why I needed a new butt? "
            "Ask me in the chat—I’ll spill the story there. Of course, the full saga "
            "is reserved for the exclusive buyers-only chat. Trust me, it’s worth it!"
        ),
    },
    "67 Coin": {
        "name": "The Official 67 Coin",
        "ticker": "$67",
        "narrative": (
            "The world’s most famous number goes fully degen. A coin for everyone "
            "who sees 67 everywhere and believes in number lore."
        ),
    },
    "Franklin The Turtle": {
        "name": "Franklin The Turtle",
        "ticker": "$FRANKLIN",
        "narrative": (
            "The childhood turtle who finally snapped and joined crypto. "
            "Immigration memes, life coping, and slow‑and‑steady degen energy."
        ),
    },
}

# ----- MAIN UI -----
st.title("💊 Meme Coin 40‑Point Scoring Vault")
st.write(
    "Score meme coin ideas, save them, and compare their virality potential over time. "
    "Built around an 8‑criterion, 40‑point model."
)

st.markdown("---")

# ----- IDEA INPUT + PRESETS -----
st.markdown("### 🧠 Idea details")

preset = st.selectbox(
    "Load a sample idea (optional)",
    list(sample_ideas.keys()),
    index=0,
)

selected = sample_ideas[preset]

idea_name = st.text_input("Idea name", value=selected["name"], placeholder="e.g., Underpaid Dev Coin")
ticker = st.text_input("Ticker", value=selected["ticker"], placeholder="e.g., $DEVGHOST")
narrative = st.text_area(
    "Core narrative (1–3 sentences)",
    value=selected["narrative"],
    height=180,
    placeholder="Describe the story, pain, or joke behind this coin."
)

st.markdown("---")

# ----- SCORING SECTION -----
st.markdown("### 🎯 Score this idea (0–5 per criterion)")
st.caption("Scoring: 0 = nonexistent, 1 = very weak, 3 = decent, 5 = elite/obvious.")

# You can change defaults if you want different starting sliders
# Meme Foundation
st.subheader("1. Meme foundation")

concept_clarity = st.slider(
    "Concept clarity – Can someone understand the meme in 3 seconds?",
    0, 5, 3
)
remixability = st.slider(
    "Remixability – How easy is it to create variations, templates, and running jokes?",
    0, 5, 3
)
cultural_bandwidth = st.slider(
    "Cultural bandwidth – Does it work across countries and cultures?",
    0, 5, 3
)

# Social Energy
st.subheader("2. Social energy")

reply_bait = st.slider(
    "Reply‑bait potential – Does it naturally invite replies, confessions, flexes, cope, or stories?",
    0, 5, 3
)
conflict_tension = st.slider(
    "Conflict / tension – Is there a clear “versus” dynamic (community vs whale, worker vs employer, etc.)?",
    0, 5, 3
)
status_signaling = st.slider(
    "Status signaling – Does holding the coin say something about the holder (I’m early, I get it, I suffer, I’m in)?",
    0, 5, 3
)

# Attention Anchors
st.subheader("3. Attention anchors")

narrative_hook = st.slider(
    "Narrative hook – Can you write a strong one‑liner headline around this coin?",
    0, 5, 3
)
character_strength = st.slider(
    "Character / symbol strength – Is there a strong visual icon, character, number, or symbol?",
    0, 5, 3
)

criteria_scores = {
    "Concept Clarity": concept_clarity,
    "Remixability": remixability,
    "Cultural Bandwidth": cultural_bandwidth,
    "Reply‑Bait Potential": reply_bait,
    "Conflict / Tension": conflict_tension,
    "Status Signaling": status_signaling,
    "Narrative Hook": narrative_hook,
    "Character / Symbol Strength": character_strength,
}
total_score = sum(criteria_scores.values())
tier = rate_score(total_score)
tier_text = tier_description(tier)

# ----- RESULTS -----
st.markdown("---")
st.markdown("### 📊 Results")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total score", f"{total_score} / 40")
with col2:
    st.metric("Tier", tier)

st.write(tier_text)

with st.expander("🔍 See detailed breakdown"):
    for name, score in criteria_scores.items():
        st.write(f"- **{name}:** {score} / 5")

# Suggestions for weak areas
st.markdown("### 🧩 Suggestions based on weak dimensions")

low_dims = [name for name, score in criteria_scores.items() if score <= 2]

if not low_dims:
    st.write("This idea is structurally solid across all dimensions. Focus now on distribution, timing, and execution.")
else:
    st.write("Consider improving these dimensions:")
    for dim in low_dims:
        if dim == "Concept Clarity":
            st.write("- **Concept Clarity:** Simplify until the idea fits in one brutal, obvious sentence.")
        elif dim == "Remixability":
            st.write("- **Remixability:** Design at least 5 meme formats, rituals, or templates people can reuse.")
        elif dim == "Cultural Bandwidth":
            st.write("- **Cultural Bandwidth:** Remove region‑locked references and use more universal pain or archetypes.")
        elif dim == "Reply‑Bait Potential":
            st.write("- **Reply‑Bait Potential:** Add prompts that naturally make people share stories, failures, or screenshots.")
        elif dim == "Conflict / Tension":
            st.write("- **Conflict / Tension:** Create a clear ‘enemy’ or opposing force your community rallies against.")
        elif dim == "Status Signaling":
            st.write("- **Status Signaling:** Make holding the coin say something about identity, taste, struggle, or being early.")
        elif dim == "Narrative Hook":
            st.write("- **Narrative Hook:** Write 5 fake headlines until one feels viral on CT/X.")
        elif dim == "Character / Symbol Strength":
            st.write("- **Character / Symbol Strength:** Attach a strong archetype, mascot, number, or visual icon people can spam.")

st.markdown("---")

# ----- SAVE IDEA -----
st.markdown("### 💾 Save this idea to your vault")

if st.button("Save / Update Idea"):
    if not idea_name:
        st.warning("You need at least an idea name to save.")
    else:
        timestamp = datetime.utcnow().isoformat() + "Z"

        new_entry = {
            "name": idea_name,
            "ticker": ticker,
            "narrative": narrative,
            "scores": criteria_scores,
            "total_score": total_score,
            "tier": tier,
            "timestamp": timestamp,
        }

        # If idea with same name exists, update it; else append
        updated = False
        for i, idea in enumerate(ideas):
            if idea["name"].strip().lower() == idea_name.strip().lower():
                ideas[i] = new_entry
                updated = True
                break
        if not updated:
            ideas.append(new_entry)

        st.session_state.ideas = ideas
        save_ideas(ideas)
        st.success("Idea saved to vault.")

# ----- IDEA VAULT / TABLE -----
st.markdown("### 📚 Idea vault")

if not ideas:
    st.info("No ideas saved yet. Score something and hit **Save / Update Idea**.")
else:
    df = pd.DataFrame([
        {
            "Name": idea["name"],
            "Ticker": idea["ticker"],
            "Total Score": idea["total_score"],
            "Tier": idea["tier"],
            "Saved At": idea.get("timestamp", ""),
        }
        for idea in ideas
    ])

    df_sorted = df.sort_values(by="Total Score", ascending=False).reset_index(drop=True)
    st.dataframe(df_sorted, use_container_width=True)

    # Basic analytics
    st.markdown("#### 📈 Tier distribution")
    tier_counts = df_sorted["Tier"].value_counts()
    st.bar_chart(tier_counts)

    # Download as CSV
    csv = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download vault as CSV",
        data=csv,
        file_name="meme_coin_ideas_vault.csv",
        mime="text/csv",
    )

st.caption("Tip: Open this on your phone too – the layout is mobile‑friendly and sliders work great on touch.")
