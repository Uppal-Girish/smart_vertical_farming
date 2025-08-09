# 1. Imports & Setup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from IPython.display import display, HTML

sns.set(style="whitegrid")

# -----------------------------
# 2. Load or Simulate Dataset
# -----------------------------

records = []

for i in range(5):
    print(f"\n📥 Entry {i + 1}")
    temp = float(input("🌡️  What was the temperature (°C)? "))
    humidity = float(input("💧 What was the humidity (%)? "))
    moisture = int(input("🌱 What was the soil moisture? "))
    distance = float(input("📏 What distance was this taken from (cm)? "))

    records.append({
        "Temperature": temp,
        "Humidity": humidity,
        "Moisture": moisture,
        "Distance": distance
    })

df = pd.DataFrame(records)

# -----------------------------
# 3. Preprocessing
# -----------------------------
df = df.drop(columns=["Timestamp"])

IDEAL_TEMP = 20
IDEAL_HUMIDITY = 50
IDEAL_MOISTURE = 300
IDEAL_DISTANCE = 5

df["HealthScore"] = 100 \
    - abs(df["Temperature"] - IDEAL_TEMP) * 1.0 \
    - abs(df["Humidity"] - IDEAL_HUMIDITY) * 0.5 \
    - abs(df["Moisture"] - IDEAL_MOISTURE) * 0.2 \
    - abs(df["Distance"] - IDEAL_DISTANCE) * 5.0

df["HealthScore"] = df["HealthScore"].clip(0, 100)

# -----------------------------
# 4. Model Training
# -----------------------------
X = df[["Temperature", "Humidity", "Moisture", "Distance"]]
y = df["HealthScore"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
display(HTML(f"<h2 style='color: darkred;'>📉 Mean Squared Error: <b>{mse:.2f}</b></h2>"))

last_row = df[["Temperature", "Humidity", "Moisture", "Distance"]].iloc[[-1]]
predicted_health = model.predict(last_row)[0]
display(HTML(f"<h2 style='color: green;'>🌿 Predicted Health Score for Last Entry: <b>{predicted_health:.2f} / 100</b></h2>"))

# -----------------------------
# 5. Visualizations
# -----------------------------

# 5.1 Actual vs Predicted Scatter Plot with Line of Best Fit
plt.figure(figsize=(6, 4))
plt.scatter(y_test, y_pred, alpha=0.7, color='mediumseagreen')
plt.plot([0, 100], [0, 100], '--', color='gray', label='Ideal Fit (y=x)')
plt.xlabel("Actual Health Score")
plt.ylabel("Predicted Health Score")
plt.title("🌿 Actual vs Predicted Plant Health")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 5.2 Distribution of Health Scores
plt.figure(figsize=(6, 4))
plt.title("📊 Distribution of Health Scores")
plt.xlabel("Health Score")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()

# 5.4 Feature vs Health Score (scatter plots) with line of best fit
features = ["Temperature", "Humidity", "Moisture", "Distance"]
colors = ["red", "blue", "orange", "purple"]

plt.figure(figsize=(12, 8))
for i, feature in enumerate(features):
    plt.subplot(2, 2, i+1)
    sns.scatterplot(x=df[feature], y=df["HealthScore"], color=colors[i])

    # Calculate line of best fit
    m, b = np.polyfit(df[feature], df["HealthScore"], 1)
    x_vals = np.array(plt.gca().get_xlim())
    y_vals = m * x_vals + b
    plt.plot(x_vals, y_vals, color='black', linestyle='--')

    plt.title(f"{feature} vs Health Score")
    plt.xlabel(feature)
    plt.ylabel("Health Score")
    plt.grid(True)
plt.tight_layout()
plt.show()