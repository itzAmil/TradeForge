#ml/explain_model.py
import os
import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

def load_data():
    data_paths = [
        "data/BTCUSDT_15m_labeled.csv",
        "data/BTCUSDT_15m.csv",
        "data/BTCUSDT_15m_predicted.csv"
    ]
    
    for path in data_paths:
        if os.path.exists(path):
            print(f"📂 Using dataset: {path}")
            df = pd.read_csv(path)

            # Drop obvious non-numeric columns
            drop_cols = [col for col in df.columns if df[col].dtype == "object"]
            if drop_cols:
                print(f"⚠️ Dropping non-numeric columns: {drop_cols}")
                df = df.drop(columns=drop_cols)

            # Drop label if exists
            if "label" in df.columns:
                df = df.drop(columns=["label"])

            # Convert to numeric and clean
            df = df.apply(pd.to_numeric, errors="coerce")
            df = df.dropna()

            return df
    
    print(f"⚠️ No dataset found. Checked paths: {data_paths}")
    return None

def load_model(model_name):
    model_paths = {
        "random_forest": "ml/model_rf.pkl",
        "xgboost": "ml/models/xgboost.pkl"
    }
    if model_name in model_paths and os.path.exists(model_paths[model_name]):
        print(f"📦 Loading model: {model_paths[model_name]}")
        return joblib.load(model_paths[model_name])
    raise FileNotFoundError(f"Model {model_name} not found at {model_paths.get(model_name)}")

def explain_with_shap(model, model_name, X):
    print(f"🔎 Explaining {model_name} using SHAP...")
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)

    os.makedirs("ml/plots", exist_ok=True)

    # 📊 Summary Plot
    plt.figure()
    shap.summary_plot(shap_values, X, show=False)
    summary_path = f"ml/plots/shap_summary_{model_name}.png"
    plt.savefig(summary_path, bbox_inches="tight")
    plt.close()
    print(f"✅ SHAP summary plot saved to {summary_path}")

def main():
    df = load_data()
    if df is None:
        return
    
    X = df  # Already cleaned
    
    for model_name in ["random_forest", "xgboost"]:
        try:
            model = load_model(model_name)
            explain_with_shap(model, model_name, X)
        except Exception as e:
            print(f"❌ Could not explain {model_name}: {e}")

if __name__ == "__main__":
    main()
