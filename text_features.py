from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


def build_text_features(texts: pd.Series, max_features: int = 3000):
    """Convert text into TF-IDF features."""
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=max_features,
    )
    X_text = vectorizer.fit_transform(texts)
    return X_text, vectorizer
