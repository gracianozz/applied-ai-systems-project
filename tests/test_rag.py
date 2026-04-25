import os
import sys
from pathlib import Path


# Set a dummy key before importing rag so model initialization does not fail in tests.
os.environ.setdefault("GEMINI_API_KEY", "test-key")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag import (  # noqa: E402
    build_prompt,
    insufficient_information_message,
    retrieve,
    retrieve_by_artist,
    should_generate_response,
    tokenize,
)


def make_song(
    *,
    title: str,
    artist: str,
    genre: str,
    energy: float,
    tempo: float,
    danceability: float,
    valence: float,
    popularity: float,
) -> dict:
    text = (
        f"Song: {title} by {artist}. "
        f"Album: Test Album. "
        f"Genre: {genre}. "
        f"Energy: {energy:.2f}. "
        f"Tempo: {tempo:.1f} BPM. "
        f"Danceability: {danceability:.2f}. "
        f"Valence: {valence:.2f}. "
        f"Popularity: {popularity}. "
        f"Playlist: Test Playlist."
    )

    return {
        "id": 1,
        "text": text,
        "title": title,
        "artist": artist,
        "genre": genre,
        "energy": energy,
        "tempo": tempo,
        "danceability": danceability,
        "valence": valence,
        "track_popularity": popularity,
    }


def test_retrieve_ranks_relevant_song_first_and_adds_scores():
    documents = [
        make_song(
            title="Blinding Lights",
            artist="The Weeknd",
            genre="pop",
            energy=0.89,
            tempo=171,
            danceability=0.51,
            valence=0.33,
            popularity=95,
        ),
        make_song(
            title="Soft Focus",
            artist="LoFi Artist",
            genre="lofi",
            energy=0.30,
            tempo=82,
            danceability=0.40,
            valence=0.60,
            popularity=50,
        ),
    ]

    results = retrieve("upbeat pop workout songs", documents, k=2)

    assert len(results) == 2
    assert results[0]["title"] == "Blinding Lights"
    assert results[0]["score"] > results[1]["score"]
    assert results[0]["score"] > 0


def test_retrieve_by_artist_returns_matching_artist_first():
    documents = [
        make_song(
            title="Starboy",
            artist="The Weeknd",
            genre="pop",
            energy=0.80,
            tempo=93,
            danceability=0.68,
            valence=0.40,
            popularity=98,
        ),
        make_song(
            title="Another Song",
            artist="Some Other Artist",
            genre="rock",
            energy=0.70,
            tempo=110,
            danceability=0.50,
            valence=0.55,
            popularity=60,
        ),
    ]

    results = retrieve_by_artist("The Weeknd", documents, k=5)

    assert len(results) == 1
    assert results[0]["artist"] == "The Weeknd"
    assert "score" not in results[0]


def test_retrieve_by_artist_includes_matching_collaboration_rows():
    documents = [
        make_song(
            title="Open Arms",
            artist="SZA, Travis Scott",
            genre="r&b",
            energy=0.52,
            tempo=120,
            danceability=0.61,
            valence=0.44,
            popularity=92,
        ),
        make_song(
            title="FE!N",
            artist="Travis Scott, Playboi Carti",
            genre="hip hop",
            energy=0.80,
            tempo=148,
            danceability=0.70,
            valence=0.55,
            popularity=95,
        ),
        make_song(
            title="Not a Match",
            artist="Travis Barker",
            genre="rock",
            energy=0.72,
            tempo=130,
            danceability=0.40,
            valence=0.50,
            popularity=75,
        ),
    ]

    results = retrieve_by_artist("Travis Scott", documents, k=5)

    assert len(results) == 2
    assert all("Travis Scott" in song["artist"] for song in results)


def test_should_generate_response_rejects_weak_results():
    weak_docs = [
        {"score": 0},
        {"score": 1},
        {"score": 0},
    ]

    assert should_generate_response(weak_docs) is False


def test_should_generate_response_accepts_strong_results():
    strong_docs = [
        {"score": 4},
        {"score": 3},
        {"score": 2},
    ]

    assert should_generate_response(strong_docs) is True


def test_should_generate_response_artist_mode_uses_count_guardrail_only():
    artist_docs = [{"title": "A"}, {"title": "B"}]

    assert should_generate_response(artist_docs, mode="artist") is True


def test_build_prompt_includes_query_and_song_titles():
    documents = [
        make_song(
            title="Blinding Lights",
            artist="The Weeknd",
            genre="pop",
            energy=0.89,
            tempo=171,
            danceability=0.51,
            valence=0.33,
            popularity=95,
        )
    ]

    prompt = build_prompt("songs for running", documents)

    assert "songs for running" in prompt
    assert "Blinding Lights" in prompt
    assert "The Weeknd" in prompt


def test_insufficient_information_message_is_clear():
    message = insufficient_information_message()

    assert isinstance(message, str)
    assert "not have enough information" in message.lower()


def test_tokenize_removes_common_stop_words():
    tokens = tokenize("Something that I can play so I will not be bored during my road trip")

    assert "i" not in tokens
    assert "my" not in tokens
    assert "that" not in tokens
    assert "so" not in tokens
    assert "be" not in tokens
    assert "will" not in tokens
    assert "something" in tokens
    assert "bored" in tokens
    assert "road" in tokens
    assert "trip" in tokens


def test_retrieve_expands_running_synonyms_for_better_match():
    documents = [
        make_song(
            title="Sprint Mode",
            artist="Cardio Crew",
            genre="edm",
            energy=0.92,
            tempo=138,
            danceability=0.76,
            valence=0.70,
            popularity=70,
        ),
        make_song(
            title="Quiet Rain",
            artist="Still Waves",
            genre="ambient",
            energy=0.20,
            tempo=78,
            danceability=0.30,
            valence=0.45,
            popularity=65,
        ),
    ]

    results = retrieve("jogging playlist", documents, k=2)

    assert results[0]["title"] == "Sprint Mode"
    assert results[0]["score"] > results[1]["score"]


def test_retrieve_expands_chill_synonyms_for_low_energy_requests():
    documents = [
        make_song(
            title="Night Study",
            artist="LoFi Notes",
            genre="lofi",
            energy=0.28,
            tempo=84,
            danceability=0.41,
            valence=0.57,
            popularity=62,
        ),
        make_song(
            title="Peak Hour",
            artist="Pulse Unit",
            genre="house",
            energy=0.88,
            tempo=128,
            danceability=0.80,
            valence=0.68,
            popularity=73,
        ),
    ]

    results = retrieve("tranquil music for reading", documents, k=2)

    assert results[0]["title"] == "Night Study"
    assert results[0]["score"] > results[1]["score"]