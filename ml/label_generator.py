# ml/label_generator.py

import pandas as pd

def assign_label(future_return: float, threshold: float) -> int:
    """
    Assign trading label based on future return and threshold.
    """
    if future_return > threshold:
        return 1   # Buy
    elif future_return < -threshold:
        return -1  # Sell
    else:
        return 0   # Hold

def generate_labels(df: pd.DataFrame, threshold: float = 0.002, future_window: int = 5) -> pd.DataFrame:
    """
    Generate labels for ML classification (+1: Buy, -1: Sell, 0: Hold) 
    based on future price returns.

    Parameters:
        df (pd.DataFrame): Input DataFrame with a 'close' column.
        threshold (float): Return threshold (e.g., 0.002 for 0.2%).
        future_window (int): How many steps into the future to look.

    Returns:
        pd.DataFrame: DataFrame with 'label' column.
    """
    df = df.copy()
    df["future_price"] = df["close"].shift(-future_window)
    df["future_return"] = (df["future_price"] - df["close"]) / df["close"]

    # Apply labeling logic
    df["label"] = df["future_return"].apply(lambda x: assign_label(x, threshold))

    # Drop intermediate cols
    df.drop(["future_price", "future_return"], axis=1, inplace=True)

    return df
