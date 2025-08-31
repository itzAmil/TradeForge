# streamlit_app/pages/10_Model_Trainer.py

import sys, os
import streamlit as st
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
import plotly.figure_factory as ff
import numpy as np

# --- Ensure project root is in sys.path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Page Config ---
st.set_page_config(page_title="ML Model Trainer", page_icon="🤖", layout="wide")
st.title("Model Trainer Pro 🤖")
st.write("Upload labeled dataset → train ML models → download trained models ✅")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload labeled CSV (must include OHLCV features + 'label')", type=["csv"])

# --- Model selection ---
st.subheader("Select Models to Train")
train_rf = st.checkbox("Random Forest 🌲", value=True)
train_xgb = st.checkbox("XGBoost ⚡", value=True)

if uploaded_file and (train_rf or train_xgb):
    df = pd.read_csv(uploaded_file).dropna()

    if 'label' not in df.columns:
        st.error("CSV must contain a 'label' column.")
    else:
        st.write("🔧 Feature Engineering...")

        # --- Handle timestamps ---
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
            df.drop(columns=['timestamp'], inplace=True)

        # --- Additional numeric features ---
        df['volatility'] = df['close'].rolling(10).std().fillna(0)
        df['momentum'] = (df['close'] - df['close'].shift(5)).fillna(0)
        df['returns'] = df['close'].pct_change().fillna(0)

        # --- Select numeric features only ---
        FEATURES = [col for col in df.columns if col != 'label' and pd.api.types.is_numeric_dtype(df[col])]
        TARGET = 'label'

        st.write("⚖️ Balancing classes via upsampling...")
        df_majority = df[df[TARGET] == 0]
        df_minority = df[df[TARGET] != 0]
        df_minority_upsampled = resample(df_minority,
                                         replace=True,
                                         n_samples=len(df_majority),
                                         random_state=42)
        df_balanced = pd.concat([df_majority, df_minority_upsampled])
        X = df_balanced[FEATURES]
        y = df_balanced[TARGET]

        # --- Map labels for XGBoost ---
        label_map = {-1: 0, 0: 1, 1: 2}
        reverse_map = {v: k for k, v in label_map.items()}
        y_mapped = y.map(label_map)

        # --- Train/test split ---
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_mapped, test_size=0.2, random_state=42, stratify=y_mapped
        )

        # --- Feature Scaling ---
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # --- Hyperparameter tuning setups ---
        rf_param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 5, 10, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        xgb_param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.7, 0.8, 1.0],
            'colsample_bytree': [0.7, 0.8, 1.0]
        }

        # --- Initialize models ---
        models = {}
        search_cv_models = {}
        if train_rf:
            rf = RandomForestClassifier(class_weight='balanced', random_state=42)
            models["Random Forest 🌲"] = rf
            search_cv_models["Random Forest 🌲"] = rf_param_grid
        if train_xgb:
            xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
            models["XGBoost ⚡"] = xgb
            search_cv_models["XGBoost ⚡"] = xgb_param_grid

        MODEL_DIR = os.path.join("ml", "models")
        os.makedirs(MODEL_DIR, exist_ok=True)

        st.subheader("📊 Training Results with Hyperparameter Tuning")

        for name, model in models.items():
            with st.spinner(f"Tuning & Training {name}..."):
                # --- Randomized Search CV ---
                param_grid = search_cv_models[name]
                search = RandomizedSearchCV(model, param_distributions=param_grid,
                                            n_iter=5, cv=3, scoring='accuracy',
                                            random_state=42, n_jobs=-1)
                search.fit(X_train, y_train)
                best_model = search.best_estimator_

                y_pred = best_model.predict(X_test)

                # Map back to original labels
                y_pred_orig = pd.Series(y_pred).map(reverse_map)
                y_test_orig = pd.Series(y_test).map(reverse_map)

                acc = accuracy_score(y_test_orig, y_pred_orig)
                report = classification_report(y_test_orig, y_pred_orig, zero_division=0)
                cm = confusion_matrix(y_test_orig, y_pred_orig, labels=[-1,0,1])

                st.success(f"✅ {name} Best Accuracy: {acc:.4f}")
                st.text(report)

                # Confusion matrix
                st.subheader(f"Confusion Matrix: {name}")
                fig = ff.create_annotated_heatmap(
                    z=cm,
                    x=["-1","0","1"],
                    y=["-1","0","1"],
                    colorscale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Save model + scaler
                model_path = os.path.join(MODEL_DIR, f"{name.replace(' ','_')}.pkl")
                joblib.dump({'model': best_model, 'scaler': scaler}, model_path)

                # Download button
                with open(model_path, "rb") as f:
                    st.download_button(
                        label=f"💾 Download {name} model + scaler",
                        data=f,
                        file_name=f"{name.replace(' ','_')}.pkl",
                        mime="application/octet-stream"
                    )
