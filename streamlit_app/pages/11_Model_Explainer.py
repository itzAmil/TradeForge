# streamlit_app/pages/11_Model_Explainer.py

import os
import sys
import streamlit as st
import pandas as pd
import joblib
import shap
import plotly.graph_objects as go
import numpy as np

# --- Ensure project root is in sys.path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- Paths ---
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'models'))

# --- Streamlit Page Config ---
st.set_page_config(page_title="ML Model Explainer", page_icon="🧩", layout="wide")
st.title("Model Explainer 🧩")
st.write("Visualize feature importance and SHAP explanations for your trained models.")

# --- Dataset Selection ---
data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
if not data_files:
    st.error(f"No CSV files found in {DATA_DIR}")
    st.stop()

selected_data = st.selectbox("Select Dataset", data_files)
df = pd.read_csv(os.path.join(DATA_DIR, selected_data)).dropna()
st.write(f"Loaded dataset: **{selected_data}** with {df.shape[0]} rows and {df.shape[1]} columns.")

# --- Model Selection ---
model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith('.pkl')]
if not model_files:
    st.error(f"No models found in {MODEL_DIR}")
    st.stop()

selected_model_file = st.selectbox("Select Model", model_files)
model = joblib.load(os.path.join(MODEL_DIR, selected_model_file))
st.write(f"Loaded model: **{selected_model_file}**")

# --- Numeric Features ---
numeric_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
if 'label' in numeric_features:
    numeric_features.remove('label')

if not numeric_features:
    st.error("No numeric features found for SHAP explanation.")
    st.stop()

st.write(f"Using numeric features: {numeric_features}")
X = df[numeric_features]

# --- SHAP Explainer ---
st.subheader("SHAP Feature Importance")
try:
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)

    # Handle multi-class
    if shap_values.values.ndim == 3:
        num_classes = shap_values.values.shape[2]
        class_idx = st.selectbox("Select Class for SHAP visualization", range(num_classes))
        shap_class_values = shap_values.values[:, :, class_idx]
    else:
        shap_class_values = shap_values.values

    # --- SHAP Summary Plot (Interactive with Plotly) ---
    st.write("### SHAP Summary Plot (Interactive)")
    mean_abs_shap = np.abs(shap_class_values).mean(axis=0)
    fig_summary = go.Figure()
    fig_summary.add_trace(go.Bar(
        x=numeric_features,
        y=mean_abs_shap,
        marker_color='teal',
        text=[f"{val:.4f}" for val in mean_abs_shap],
        textposition='auto',
        hovertemplate="%{x}<br>Mean |SHAP|: %{y:.4f}<extra></extra>"
    ))
    fig_summary.update_layout(
        title="Mean Absolute SHAP Values",
        xaxis_title="Features",
        yaxis_title="Mean |SHAP|",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_summary, use_container_width=True)

    # --- Top SHAP Features Table (Interactive & Sortable) ---
    st.subheader("Top SHAP Features")
    top_shap_df = pd.DataFrame({
        'Feature': numeric_features,
        'Mean Absolute SHAP': mean_abs_shap
    }).sort_values(by='Mean Absolute SHAP', ascending=False)
    st.dataframe(top_shap_df)  # Streamlit allows interactive sorting

    # --- SHAP Dependence Plots (Interactive with Plotly) ---
    st.write("### SHAP Dependence Plots (Interactive)")
    for feature in numeric_features:
        st.write(f"#### {feature}")
        fig_dep = go.Figure()
        shap_vals_feat = shap_class_values[:, numeric_features.index(feature)]
        fig_dep.add_trace(go.Scatter(
            x=X[feature],
            y=shap_vals_feat,
            mode='markers',
            marker=dict(
                size=6,
                color=shap_vals_feat,
                colorscale='Viridis',
                showscale=True
            ),
            text=[f"{feature}: {val:.4f}<br>SHAP: {shap:.4f}" 
                  for val, shap in zip(X[feature], shap_vals_feat)],
            hoverinfo='text'
        ))
        fig_dep.update_layout(
            title=f"SHAP Dependence Plot: {feature}",
            xaxis_title=feature,
            yaxis_title="SHAP Value"
        )
        st.plotly_chart(fig_dep, use_container_width=True)

except Exception as e:
    st.error(f"SHAP explanation failed: {e}")
