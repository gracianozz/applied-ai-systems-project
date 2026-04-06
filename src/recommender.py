import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []

    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        print(f"Loading songs from {csv_path}...")

        for row in reader:
            parsed_row: Dict = {}
            for key, value in row.items():
                if value is None:
                    parsed_row[key] = value
                    continue

                raw_value = value.strip()
                if raw_value == "":
                    parsed_row[key] = raw_value
                    continue

                try:
                    parsed_row[key] = int(raw_value)
                    continue
                except ValueError:
                    pass

                try:
                    parsed_row[key] = float(raw_value)
                    continue
                except ValueError:
                    pass

                parsed_row[key] = raw_value

            songs.append(parsed_row)

    return songs

def score_song(song: Dict, user_prefs: Dict, tempo_min: float, tempo_max: float) -> Tuple[float, str]:
    """Score a song against user preferences using genre, mood, energy, and tempo similarity."""
    """
    
    Functional implementation of the recommendation logic.
    Uses weighted point system (0-10 scale) with genre, mood, energy, and tempo.
    Required by src/main.py
    """
    # Scoring weights (sum to 10)
    GENRE_WEIGHT = 3.0
    MOOD_WEIGHT = 2.5
    ENERGY_WEIGHT = 2.5
    TEMPO_WEIGHT = 2.0

    target_genre = str(user_prefs.get("genre", "")).lower().strip()
    target_mood = str(user_prefs.get("mood", "")).lower().strip()
    target_energy = float(user_prefs.get("energy", 0.5))
    target_tempo = float(user_prefs.get("tempo_bpm", 100))

    tempo_range = tempo_max - tempo_min if tempo_max != tempo_min else 1
    target_tempo_norm = (target_tempo - tempo_min) / tempo_range

    explanation_parts = []
    total_score = 0.0

    # Genre scoring
    song_genre = str(song.get("genre", "")).lower().strip()
    if song_genre == target_genre:
        genre_points = GENRE_WEIGHT
        explanation_parts.append(f"genre match (+{genre_points})")
        total_score += genre_points

    # Mood scoring
    song_mood = str(song.get("mood", "")).lower().strip()
    if song_mood == target_mood:
        mood_points = MOOD_WEIGHT
        explanation_parts.append(f"mood match (+{mood_points})")
        total_score += mood_points

    # Energy scoring
    song_energy = float(song.get("energy", 0.5))
    energy_similarity = 1 - abs(song_energy - target_energy)
    energy_points = ENERGY_WEIGHT * energy_similarity
    total_score += energy_points
    explanation_parts.append(f"energy closeness (+{energy_points:.2f})")

    # Tempo scoring
    song_tempo = float(song.get("tempo_bpm", 0))
    song_tempo_norm = (song_tempo - tempo_min) / tempo_range
    tempo_similarity = 1 - abs(song_tempo_norm - target_tempo_norm)
    tempo_points = TEMPO_WEIGHT * tempo_similarity
    total_score += tempo_points
    explanation_parts.append(f"tempo closeness (+{tempo_points:.2f})")

    return total_score, ", ".join(explanation_parts)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Recommend the top k songs for a user by scoring and ranking the available songs."""

    """
    Functional implementation of the recommendation logic.
    Uses score_song(...) for per-song scoring, then ranks by score.
    Required by src/main.py
    """
    tempos = [float(song.get("tempo_bpm", 0)) for song in songs if song.get("tempo_bpm") is not None]
    tempo_min = min(tempos) if tempos else 58
    tempo_max = max(tempos) if tempos else 152

    scored_songs = sorted(
        (
            (song, *score_song(song, user_prefs, tempo_min, tempo_max))
            for song in songs
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    return scored_songs[:k]

