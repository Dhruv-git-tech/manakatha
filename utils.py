import random, json, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from indicnlp.normalize.indic_normalize import IndicNormalizer
from emoji import emojize

MODEL_NAME = "ai4bharat/indic-bert"          # multilingual BERT
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=3
)  # 0=negative, 1=neutral, 2=positive

normalizer = IndicNormalizer(lang="te")

COMPLIMENTS = [
    "అద్భుతమైన కథ! హృదయాన్ని తాకింది.",
    "మీరు చెప్పిన విషయం చాలా బాగుంది.",
    "అద్భుతం! భావోద్వేగాలు అద్భుతంగా వ్యక్తమయ్యాయి.",
    "మీ అనుభవం అందరినీ ప్రభావితం చేస్తుంది.",
    "చాలా హృద్యంగా ఉంది – ధన్యవాదాలు పంచుకున్నందుకు."
]

def normalize(text: str) -> str:
    return normalizer.normalize(text)

def get_sentiment(text: str) -> str:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
    label = int(logits.argmax(-1))
    return {0: "😔", 1: "😐", 2: "😊"}[label]

def get_compliment() -> str:
    return random.choice(COMPLIMENTS)

def get_rating(text: str) -> float:
    """
    Dummy rule-based rating for MVP:
    (length + unique words + positive sentiment) → 1-5 stars
    """
    text = normalize(text)
    length = min(len(text) / 200, 1.0)
    unique = min(len(set(text)) / 100, 1.0)
    sentiment = 1.0 if get_sentiment(text) == "😊" else 0.5
    score = (length + unique + sentiment) / 3 * 5
    return round(score, 1)

def load_stories():
    try:
        with open("stories.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_stories(stories):
    with open("stories.json", "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)
