"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 
    
    print("Loaded songs:",len(songs))

    # Starter example profile
    user_prefs = {"genre": "lofi", "mood": "chill", "energy": .4, "tempo_bmp": 90}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        song, score, explanation = rec
        title = song["title"] if isinstance(song, dict) else str(song)
        print(f"Title: {title}")
        print(f"Final score: {score:.2f}")
        print(f"Reasoning: {explanation}")
        print()


if __name__ == "__main__":
    main()

