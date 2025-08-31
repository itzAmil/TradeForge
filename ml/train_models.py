# ml/train_models.py

import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# === Paths ===
DATA_PATH = "data/BTCUSDT_15m_labeled.csv"
MODEL_DIR = "ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)

# === Features / Target ===
FEATURES = [
    'sma', 'ema', 'rsi', 'macd',
    'signal_line', 'bollinger_upper',
    'bollinger_lower', 'returns'
]
TARGET = 'label'

# === Load Data ===
df = pd.read_csv(DATA_PATH)
df.dropna(subset=FEATURES + [TARGET], inplace=True)

# Map labels to 0/1/2 for ML models
label_map = {-1: 0, 0: 1, 1: 2}
reverse_map = {v: k for k, v in label_map.items()}
df[TARGET] = df[TARGET].map(label_map)

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Define Models ===
models = {
    "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "xgboost": XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42
    )
}

# === Training Loop ===
for name, model in models.items():
    print(f"\n🔁 Training: {name}")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_true_mapped = y_test.map(reverse_map)
    y_pred_mapped = pd.Series(y_pred).map(reverse_map)

    acc = accuracy_score(y_true_mapped, y_pred_mapped)
    report = classification_report(y_true_mapped, y_pred_mapped)

    print(f"✅ {name} Accuracy: {acc:.4f}")
    print(report)

    # Save model
    model_path = os.path.join(MODEL_DIR, f"{name}.pkl")
    joblib.dump(model, model_path)
    print(f"💾 Saved model: {model_path}")
