import os
import re
from pathlib import Path

import google.genai as genai
import pandas as pd
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
ENV_PATHS = [SRC_DIR / ".env", PROJECT_ROOT / ".env"]
MODE_THRESHOLD_RULES = {
	"describe": {
		"min_retrieved_songs": 3,
		"min_average_score": 2.0,
	},
	"artist": {
		"min_retrieved_songs": 2,
		"min_average_score": 1.5,
	},
}

# Query expansion groups used to catch common synonym variants.
SYNONYM_GROUPS = [
	{"workout", "gym", "exercise", "training", "pump", "hype"},
	{"running", "jogging", "cardio", "sprinting"},
	{"chill", "calm", "relax", "relaxing", "study", "focus", "reading", "tranquil"},
	{"sleep", "bedtime", "night", "drowsy"},
	{"dance", "dancing", "club", "move", "groove"},
	{"happy", "upbeat", "uplifting", "positive", "cheerful", "joyful"},
	{"sad", "moody", "emotional", "melancholy", "heartbreak"},
	{"fast", "quick", "high-tempo", "energetic"},
	{"slow", "mellow", "soft", "laidback"},
]


def build_synonym_index(groups: list[set[str]]) -> dict[str, set[str]]:
	"""Build token -> synonym set mapping from groups."""
	index: dict[str, set[str]] = {}
	for group in groups:
		for token in group:
			index[token] = set(group) - {token}
	return index


SYNONYM_INDEX = build_synonym_index(SYNONYM_GROUPS)

#Set of filler words to exclude from tokenization and scoring
STOP_WORDS = {
	"a",
	"an",
	"and",
	"are",
	"as",
	"at",
	"be",
	"because",
	"been",
	"but",
	"by",
	"can",
	"do",
	"for",
	"from",
	"had",
	"has",
	"have",
	"he",
	"her",
	"here",
	"him",
	"his",
	"i",
	"if",
	"in",
	"into",
	"is",
	"it",
	"its",
	"just",
	"me",
	"my",
	"of",
	"on",
	"or",
	"our",
	"so",
	"she",
	"that",
	"the",
	"their",
	"them",
	"there",
	"they",
	"this",
	"to",
	"too",
	"up",
	"us",
	"was",
	"we",
	"were",
	"what",
	"when",
	"where",
	"which",
	"who",
	"will",
	"with",
	"you",
	"your",
}


def initialize_model(api_key: str | None = None) -> genai.Client:
	"""Load env vars, configure Gemini, and return a ready-to-use model."""
	for env_path in ENV_PATHS:
		if env_path.exists():
			load_dotenv(dotenv_path=env_path)
			break

	api_key = api_key or os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise ValueError(
			"GEMINI_API_KEY not found. Add it to src/.env or project .env as GEMINI_API_KEY=your_key_here"
		)

	return genai.Client(api_key=api_key)


model = initialize_model()


def generate_ai_response(prompt: str, model_name: str = "gemini-2.5-flash") -> str:
	"""Generate text from Gemini using the configured client."""
	response = model.models.generate_content(model=model_name, contents=prompt)
	return getattr(response, "text", "") or "No response generated."


def load_dataset(csv_path: str) -> pd.DataFrame:
	"""Load a CSV file from the data folder into a pandas DataFrame."""
	data_path = PROJECT_ROOT / csv_path
	return pd.read_csv(data_path)


def load_songs(csv_path: str = "data/high_popularity_spotify_data.csv") -> list[dict]:
	"""Load songs from Spotify CSV and return list of documents."""
	df = load_dataset(csv_path)
	documents = []
	
	for idx, row in df.iterrows():
		# Format song information as a text document
		text = (
			f"Song: {row['track_name']} by {row['track_artist']}. "
			f"Album: {row['track_album_name']}. "
			f"Genre: {row['genre']}. "
			f"Energy: {row['energy']:.2f}. "
			f"Tempo: {row['tempo']:.1f} BPM. "
			f"Danceability: {row['danceability']:.2f}. "
			f"Valence: {row['valence']:.2f}. "
			f"Popularity: {row['track_popularity']}. "
			f"Playlist: {row['playlist_name']}."
		)
		
		# Create document dictionary
		doc = {
			'id': idx,
			'text': text,
			'title': row['track_name'],
			'artist': row['track_artist'],
			'genre': str(row['genre']).lower(),
			'energy': float(row['energy']),
			'tempo': float(row['tempo']),
			'danceability': float(row['danceability']),
			'valence': float(row['valence']),
			'track_popularity': float(row['track_popularity'])
		}
		documents.append(doc)
	
	return documents


def tokenize(text: str) -> set[str]:
	"""Convert text into lowercase word tokens with punctuation removed."""
	tokens = re.findall(r"[a-z0-9]+", text.lower())
	return {token for token in tokens if token not in STOP_WORDS}


def normalize_text(text: str) -> str:
	"""Convert text into a normalized lowercase string for exact matching."""
	return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def expand_query_tokens(query_tokens: set[str]) -> set[str]:
	"""Expand tokens with configured synonyms to improve recall."""
	expanded_tokens = set(query_tokens)
	for token in list(query_tokens):
		expanded_tokens.update(SYNONYM_INDEX.get(token, set()))
	return expanded_tokens


def score_document(query_tokens: set[str], doc: dict) -> int:
	"""Score one document using token overlap + keyword-based rule bonuses."""
	doc_tokens = tokenize(doc["text"])
	base_score = len(query_tokens.intersection(doc_tokens))
	rule_bonus = 0

	# Energy intent rules
	if query_tokens.intersection({"workout", "gym", "intense", "hype", "party", "pump"}) and doc["energy"] >= 0.75:
		rule_bonus += 3
	if query_tokens.intersection({"chill", "calm", "relax", "study", "sleep", "focus"}) and doc["energy"] <= 0.45:
		rule_bonus += 3

	# Danceability and mood rules
	if query_tokens.intersection({"dance", "club", "move", "groove"}) and doc["danceability"] >= 0.70:
		rule_bonus += 2
	if query_tokens.intersection({"happy", "upbeat", "uplifting", "positive", "cheerful"}) and doc["valence"] >= 0.65:
		rule_bonus += 2
	if query_tokens.intersection({"sad", "moody", "emotional", "melancholy"}) and doc["valence"] <= 0.40:
		rule_bonus += 2

	# Tempo rules
	if query_tokens.intersection({"fast", "running", "cardio", "energetic"}) and doc["tempo"] >= 120:
		rule_bonus += 2
	if query_tokens.intersection({"slow", "mellow", "bedtime", "soft"}) and doc["tempo"] <= 95:
		rule_bonus += 2

	# Genre rule: exact token match with genre terms in document
	if query_tokens.intersection(tokenize(doc["genre"])):
		rule_bonus += 3

	# Keep rule influence bounded so long queries do not dominate.
	rule_bonus = min(rule_bonus, 8)
	return base_score + rule_bonus

#Option 1: General retrieval with keyword rules
def retrieve(query: str, documents: list[dict], k: int = 5) -> list[dict]:
	"""Return top-k documents ranked by scoring function with keyword rules."""
	query_tokens = expand_query_tokens(tokenize(query))
	scored_docs = []

	for doc in documents:
		score = score_document(query_tokens, doc)

		scored_doc = {**doc, "score": score}
		scored_docs.append(scored_doc)

	scored_docs.sort(key=lambda item: item["score"], reverse=True)
	return scored_docs[:k]

#Option 2: Artist-specific retrieval
def retrieve_by_artist(artist_query: str, documents: list[dict], k: int | None = None) -> list[dict]:
	"""Return songs whose artist tokens contain all query artist tokens."""
	artist_query_clean = artist_query.strip().lower()
	if not artist_query_clean:
		return []

	artist_query_tokens = tokenize(artist_query_clean)
	if not artist_query_tokens:
		return []

	matched_docs = []

	for doc in documents:
		doc_artist = str(doc.get("artist", ""))
		doc_artist_tokens = tokenize(doc_artist)

		if artist_query_tokens.issubset(doc_artist_tokens):
			matched_docs.append(doc)

	if k is None:
		return matched_docs

	return matched_docs[:k]


def get_mode_thresholds(mode: str) -> dict[str, float]:
	"""Return retrieval thresholds for the selected UI mode."""
	return MODE_THRESHOLD_RULES.get(mode, MODE_THRESHOLD_RULES["describe"])


def should_generate_response(top_docs: list[dict], mode: str = "describe") -> bool:
	"""Return True only when retrieval produced enough signal to answer safely."""
	thresholds = get_mode_thresholds(mode)
	min_retrieved_songs = int(thresholds["min_retrieved_songs"])
	min_average_score = float(thresholds["min_average_score"])

	if len(top_docs) < min_retrieved_songs:
		return False

	if mode == "artist":
		return True

	average_score = sum(doc.get("score", 0) for doc in top_docs) / len(top_docs)
	return average_score >= min_average_score


def insufficient_information_message() -> str:
	"""Return a user-facing fallback for weak retrieval results."""
	return (
		"I do not have enough information to make a confident recommendation. "
		"Try giving me a more specific mood, genre, activity, or tempo preference."
	)


def build_prompt(query: str, top_docs: list[dict]) -> str:
	"""Build a grounded prompt from user query and top retrieved songs."""
	context_lines = []
	for i, doc in enumerate(top_docs, start=1):
		context_lines.append(
			f"{i}. Title: {doc['title']} | Artist: {doc['artist']} | "
			f"Genre: {doc['genre']} | Energy: {doc['energy']:.2f} | "
			f"Tempo: {doc['tempo']:.1f} | Danceability: {doc['danceability']:.2f} | "
			f"Valence: {doc['valence']:.2f} | Score: {doc.get('score', 0)}"
		)

	context_block = "\n".join(context_lines) if context_lines else "No matching songs were retrieved."

	prompt = (
		"You are a music recommendation assistant. Use only the songs in the context section. "
		"Do not invent song details. If context is insufficient, say so clearly.\n\n"
		f"User query:\n{query}\n\n"
		f"Retrieved songs:\n{context_block}\n\n"
		"Keep it in a concise list format with the song names and then the explanation of why they fit the query." \
		" Make the Song Names Bold and the artist italicized., then under them as a bullet point list the reasons why the song fits the query based on the retrieved features. "
		"Recommend up to 5 songs that best fit the user's request based on the retrieved information. "
		"Do not include the raw numeric values of each feature."
		"If the user query is an artist name, recommend 5 songs the songs retrieved that include that artist."
	)

	return prompt


if __name__ == "__main__":
	# Test load_songs function
	docs = load_songs()
	print(f"Loaded {len(docs)} songs from Spotify data.\n")
	print("First 2 song documents:\n")
	for doc in docs[:2]:
		print(f"ID: {doc['id']}")
		print(f"Text: {doc['text']}\n")

