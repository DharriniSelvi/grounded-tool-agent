"""Local knowledge tools for Tool Using Agent Pro."""
import json
import re
from pathlib import Path

KNOWLEDGE_FILE = Path(__file__).parent / "knowledge.json"
STOP_WORDS = {
    "what", "who", "when", "where", "why", "how", "is", "are", "the", "a", "an",
    "of", "for", "to", "in", "on", "tell", "me", "about", "please", "explain",
    "describe", "give", "details", "does", "do", "can", "you", "search", "find",
    "look", "up", "information", "and", "with", "from", "it", "this", "that"
}

def load_knowledge():
    try:
        with KNOWLEDGE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, dict)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_knowledge(data):
    with KNOWLEDGE_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def tokenize(text):
    return set(re.findall(r"[a-z0-9+#.-]+", str(text).lower()))

def list_topics():
    topics = sorted({x.get("topic", "") for x in load_knowledge() if x.get("topic")})
    return {"found": bool(topics), "topics": topics, "entries": []}

def _search(query, limit=5):
    data = load_knowledge()
    terms = tokenize(query) - STOP_WORDS
    scored = []
    for item in data:
        searchable = " ".join([
            item.get("topic", ""), item.get("question", ""),
            item.get("answer", ""), " ".join(item.get("keywords", []))
        ])
        words = tokenize(searchable)
        overlap = terms & words
        score = len(overlap)
        if score:
            # Small bonus when query terms appear in the topic name.
            score += 2 * len(terms & tokenize(item.get("topic", "")))
            scored.append((score, item))
    scored.sort(key=lambda x: (-x[0], x[1].get("topic", "").lower()))
    return [item for score, item in scored[:limit]]

def search_knowledge(query):
    entries = _search(query)
    return {"found": bool(entries), "entries": entries, "topics": []}

def get_topic_details(question):
    entries = _search(question, limit=3)
    return {"found": bool(entries), "entries": entries, "topics": []}

def add_knowledge_entry(entry):
    """Validate and persist one user-supplied trusted knowledge entry."""
    if not isinstance(entry, dict):
        raise ValueError("Entry must be a dictionary.")
    topic = str(entry.get("topic", "")).strip()
    answer = str(entry.get("answer", "")).strip()
    if not topic or not answer:
        raise ValueError("Topic and answer are required.")
    data = load_knowledge()
    normalized_topic = topic.casefold()
    if any(str(x.get("topic", "")).casefold() == normalized_topic for x in data):
        raise ValueError("A topic with this name already exists. Choose a unique topic name.")
    clean_entry = {
        "topic": topic,
        "question": str(entry.get("question", "")).strip(),
        "answer": answer,
        "keywords": [str(k).strip() for k in entry.get("keywords", []) if str(k).strip()]
    }
    data.append(clean_entry)
    save_knowledge(data)
    return clean_entry

def get_knowledge_stats():
    data = load_knowledge()
    topics = {x.get("topic", "") for x in data if x.get("topic")}
    keywords = {k.lower() for x in data for k in x.get("keywords", []) if k}
    return {"entries": len(data), "topics": len(topics), "keywords": len(keywords)}
