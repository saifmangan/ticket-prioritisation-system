import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

DATA_PATH = Path("data/processed/clean_tickets.csv")

def load_data():
    return pd.read_csv(DATA_PATH)

def train_model(df: pd.DataFrame):
    feature_cols = [
        "feat_char_len",
        "feat_words",
        "feat_excl",
        "feat_urgent",
        "feat_positive"
    ]

    X = df[feature_cols]
    y = df["priority"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\nModel Evaluation:\n")
    print(classification_report(y_test, y_pred))

    return model

def main():
    df = load_data()
    train_model(df)

if __name__ == "__main__":
    main()