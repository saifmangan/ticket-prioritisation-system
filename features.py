import re
import pandas as pd

URGENT_WORDS = {
    "urgent",
    "asap",
    "immediately",
    "now",
    "help",
    "cannot",
    "can't",
    "not working",
    "down",
    "error",
    "failed",
    "issue",
    "problem",
    "login",
    "critical",
    "pressing",
    "priority",
    "instant",
    "quickly",
    "unable",
    "blocked",
    "broken",
    "offline",
    "outage",
    "fault",
    "crash",
    "anomaly",
    "glitch",
    "bug",
    "credentials",
    "access",
    "auth",
    "assistance",
    "support",
}

POSITIVE_WORDS = {"thanks", "thank", "great", "good", "appreciate"}


def count_exclamation(text: str) -> int:
    return text.count("!")


def text_length(text: str) -> int:
    return len(text)


def word_count(text: str) -> int:
    return len(text.split())


def contains_urgent_words(text: str) -> int:
    t = text.lower()
    pattern = r"\b(" + "|".join(map(re.escape, URGENT_WORDS)) + r")\b"
    return int(bool(re.search(pattern, t)))


def contains_positive_words(text: str) -> int:
    t = text.lower()
    return int(any(w in t for w in POSITIVE_WORDS))


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    msg = df["customer_message"].fillna("").astype(str)

    df["feat_char_len"] = msg.apply(text_length)
    df["feat_words"] = msg.apply(word_count)
    df["feat_excl"] = msg.apply(count_exclamation)
    df["feat_urgent"] = msg.apply(contains_urgent_words)
    df["feat_positive"] = msg.apply(contains_positive_words)

    return df
