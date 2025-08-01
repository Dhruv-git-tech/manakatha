import streamlit as st
from utils import (
    normalize,
    get_compliment,
    get_sentiment,
    get_rating,
    load_stories,
    save_stories,
)

st.set_page_config(
    page_title="ManaKatha – మన కథ",
    page_icon="📚",
    layout="centered",
)

st.title("📚 ManaKatha – మన కథ")
st.subheader("భావోద్వేగాలను పంచుకునే తెలుగు కథల వేదిక")

# Sidebar
with st.sidebar:
    st.markdown("### శోధన")
    category_filter = st.selectbox(
        "వర్గం ప్రకారం చూడు",
        ["అన్నీ", "బాల్యం", "ప్రేమ", "పోరాటం", "ఫన్నీ మోమెంట్స్"],
    )
    show_private = st.checkbox("నా కథలు మాత్రమే చూపించు", value=False)

stories = load_stories()

# Filter
if category_filter != "అన్నీ":
    stories = [s for s in stories if s["category"] == category_filter]
if show_private and "user_id" in st.session_state:
    stories = [s for s in stories if s.get("author") == st.session_state["user_id"]]

# Tabs
tab_share, tab_archive = st.tabs(["✍️ కథ పంచుకోండి", "📚 కథల ఆర్కైవ్"])

with tab_share:
    with st.form("story_form"):
        title = st.text_input("శీర్షిక (ఐచ్చికం)")
        body = st.text_area("మీ కథ ఇక్కడ రాయండి...", height=250, max_chars=2000)
        category = st.selectbox(
            "వర్గం",
            ["బాల్యం", "ప్రేమ", "పోరాటం", "ఫన్నీ మోమెంట్స్"],
        )
        is_public = st.checkbox("ఈ కథను అందరికీ చూపించు", value=True)
        submitted = st.form_submit_button("పంపించు")

    if submitted and body.strip():
        story = {
            "title": title.strip() or "శీర్షిక లేదు",
            "body": normalize(body.strip()),
            "category": category,
            "author": st.session_state.get("user_id", "guest"),
            "public": is_public,
            "compliment": get_compliment(),
            "sentiment_emoji": get_sentiment(body),
            "rating": get_rating(body),
        }
        stories.append(story)
        save_stories(stories)
        st.success("మీ కథ విజయవంతంగా పంపబడింది!")

with tab_archive:
    if not stories:
        st.info("ఇంకా కథలేమీ లేవు.")
    else:
        for idx, story in enumerate(stories):
            if not story["public"] and story.get("author") != st.session_state.get("user_id"):
                continue
            with st.expander(
                f"{story['title']} – ⭐ {story['rating']} {story['sentiment_emoji']}"
            ):
                st.write(story["body"])
                st.caption(f"వర్గం: {story['category']} | {story['compliment']}")
                # Placeholder for Likes/Comments in v2
