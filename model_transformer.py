# model_transformer.py
import torch
import torch.nn as nn
import numpy as np
import pandas as pd

class PriceTransformer(nn.Module):
    def __init__(self, seq_len=30, d_model=32, nhead=2, num_layers=2):
        super().__init__()
        self.embed = nn.Linear(1, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, 1)

    def forward(self, x):
        x = self.embed(x)
        encoded = self.encoder(x)
        return self.fc(encoded[:, -1, :])


def add_transformer_prediction(df, price_col):
    df = df.copy()
    if len(df) < 90:
        df["tf_signal"] = "HOLD"
        df["tf_prob"] = 0.5
        return df
    
    if price_col not in df.columns:
        raise KeyError(f"Price column '{price_col}' not found in DataFrame")
    
    try:
        prices = df[price_col].values
        returns = np.diff(prices) / prices[:-1]
        returns = np.concatenate([[0], returns])

        seq_len = 30
        X, y = [], []

        for i in range(len(returns) - seq_len - 1):
            X.append(returns[i:i+seq_len])
            y.append(returns[i+seq_len])

        X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
        y = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

        model = PriceTransformer()
        optim = torch.optim.Adam(model.parameters(), lr=0.005)
        loss_fn = nn.MSELoss()

        model.train()
        for _ in range(40):
            optim.zero_grad()
            pred = model(X)
            loss = loss_fn(pred, y)
            loss.backward()
            optim.step()

        model.eval()
        test_input = torch.tensor([returns[-seq_len:]], dtype=torch.float32).unsqueeze(-1)
        pred = model(test_input).item()
        prob = 1 / (1 + np.exp(-pred * 8))

        df["tf_prob"] = prob
        df["tf_signal"] = "BUY" if prob >= 0.55 else "SELL"
        return df
    
    except Exception as e:
        # Fallback to neutral prediction if transformer fails
        print(f"Transformer prediction failed: {e}")
        df["tf_signal"] = "HOLD"
        df["tf_prob"] = 0.5
        return df
