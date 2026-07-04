import matplotlib
matplotlib.use("Agg")   # Без GUI

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("meteora_positions.csv")

result1 = df.loc[df["position"] == "4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq", "Current_deposit"]
deposit1 = df.loc[df["position"] == "4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq", "depositUsd"]
result2 = df.loc[df["position"] == "ERosWZ9LhHam5cku1pgKycVQrofpVpmi7wGSXdxJ79bo", "Current_deposit"]
deposit2 = df.loc[df["position"] == "ERosWZ9LhHam5cku1pgKycVQrofpVpmi7wGSXdxJ79bo", "depositUsd"]
date = df.loc[df["position"] == "4Rjkrs2p8n2kcTbd8KLTY3BQ9wtps4uaWjfmNfdvF4xq", "date"].str[:10]
print(date)
plt.figure(figsize=(14, 7))
plt.plot(date.values, result1.values, color="blue", linewidth=1)
plt.plot(date.values, deposit1.values, color="blue", linestyle="--", linewidth=1)
plt.plot(date.values, result2.values, color="red", linewidth=1)
plt.plot(date.values, deposit2.values, color="red", linestyle="--", linewidth=1)
plt.plot(date.values, result1.values + result2.values, color="black", linewidth=2)
plt.plot(date.values, deposit1.values + deposit2.values, linestyle="--", color="green", linewidth=1)
plt.xticks(rotation=45)
#plt.xlim(pd.Timestamp("2026-01-01"), date.max())
plt.savefig("plot.png", dpi=200)
