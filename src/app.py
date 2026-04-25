"""Streamlit UI for the RAG-based music recommendation system."""

import random

import streamlit as st

from rag import (
    build_prompt,
    generate_ai_response,
    insufficient_information_message,
    load_songs,
    retrieve,
    retrieve_by_artist,
    should_generate_response,
)


@st.cache_data
def get_documents() -> list[dict]:
    """Load and cache song documents for the UI session."""
    return load_songs("data/high_popularity_spotify_data.csv")


def generate_answer(prompt: str) -> str:
    """Call Gemini and return text output."""
    return generate_ai_response(prompt)


def run_describe_mode(documents: list[dict]) -> None:
    """Handle free-form recommendation queries."""
    query = st.text_input(
        "Describe what you want to listen to",
        placeholder="Example: Something chill for studying late at night",
        key="describe_query",
    )

    if st.button("Get Recommendations", key="describe_submit"):
        if not query.strip():
            st.info("Please enter a request first.")
            return

        top_docs = retrieve(query, documents, k=5)

        if not should_generate_response(top_docs, mode="describe"):
            st.warning(insufficient_information_message())
            return

        prompt = build_prompt(query, top_docs)
        with st.spinner("Generating recommendations..."):
            answer = generate_answer(prompt)

        st.subheader("AMPED Recommends...")
        st.write(answer)


def run_artist_mode(documents: list[dict]) -> None:
    """Handle artist-specific recommendation queries."""
    artist_query = st.text_input(
        "Enter artist name",
        placeholder="Example: The Weeknd",
        key="artist_query",
    )

    if st.button("Find Artist Songs", key="artist_submit"):
        if not artist_query.strip():
            st.info("Please enter an artist name first.")
            return

        matched_docs = retrieve_by_artist(artist_query, documents, k=None)

        if not matched_docs:
            st.warning("I could not find songs for that artist in the current dataset.")
            return

        if not should_generate_response(matched_docs, mode="artist"):
            st.warning(insufficient_information_message())
            return

        top_docs = random.sample(matched_docs, k=min(5, len(matched_docs)))

        query = f"Recommend up to 5 songs by {artist_query}."
        prompt = build_prompt(query, top_docs)

        with st.spinner("Generating recommendations..."):
            answer = generate_answer(prompt)

        st.subheader("AMPED Recommends...")
        st.write(answer)


def main() -> None:
    """Render app layout and route to selected mode."""
    st.set_page_config(page_title="AMPED", page_icon="🎵", layout="wide")

    st.markdown(
        """
        <style>
        .app-title {
            text-align: center;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .app-caption {
            text-align: center;
            font-size: 1.05rem;
            margin-bottom: 1rem;
            color: rgba(49, 51, 63, 0.8);
        }

        .mode-shell {
            max-width: 760px;
            margin: 0 auto 1.5rem auto;
        }

        div[data-testid="stRadio"] {
            display: flex;
            justify-content: center;
        }

        div[data-testid="stRadio"] > label {
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="app-title">AMPED⚡ The AI DJ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-caption">The AI DJ that knows your vibe 🎧</div>',
        unsafe_allow_html=True,
    )

    try:
        documents = get_documents()
    except Exception as exc:  # pragma: no cover
        st.error(f"Could not load song data: {exc}")
        st.stop()

    _, center_column, _ = st.columns([1, 2, 1])
    with center_column:
        st.markdown('<div class="mode-shell">', unsafe_allow_html=True)
        st.write(f"Songs loaded: {len(documents)}")
        mode = st.radio(
            "Choose mode",
            [
                "Describe what you want",
                "Artist-specific recommendations",
            ],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if mode == "Describe what you want":
        run_describe_mode(documents)
    else:
        run_artist_mode(documents)


if __name__ == "__main__":
    main()
