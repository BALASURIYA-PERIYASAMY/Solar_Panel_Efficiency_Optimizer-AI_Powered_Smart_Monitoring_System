import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("🔆 SOLAR PANEL PERFORMANCE ANALYSIS & ANOMALY DETECTION 🔆")
print("="*70)

# 1. Load the generated synthetic data
print("\n📊 Loading solar sensor data...")
data = pd.read_csv('solar_data_generated.csv')

print(f"✅ Loaded {len(data)} records")
print(f"\n📋 Dataset Columns: {list(data.columns)}")
print(f"\n🔍 Sample Data (first 5 rows):")
print(data.head())

# 2. Data Preparation
print("\n" + "-"*70)
print("🔧 PREPARING DATA FOR MODEL TRAINING")
print("-"*70)

# Use the correct column names from the generated data
X = data[['light_intensity', 'temperature']]
y = data['actual_power']

# Convert to numeric (handle any non-numeric values)
X = X.apply(pd.to_numeric, errors='coerce')
y = pd.to_numeric(y, errors='coerce')

# Drop rows with NaN values
valid_idx = X.notna().all(axis=1) & y.notna()
X_clean = X[valid_idx]
y_clean = y[valid_idx]

print(f"✅ Valid records after cleaning: {len(X_clean)}")
print(f"📌 Features (X) shape: {X_clean.shape}")
print(f"📌 Target (y) shape: {y_clean.shape}")

# 3. Train the Linear Regression Model
print("\n" + "-"*70)
print("🤖 TRAINING LINEAR REGRESSION MODEL")
print("-"*70)

X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

# Model Performance
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print(f"✅ Model trained successfully!")
print(f"📊 Training R² Score: {train_score:.4f}")
print(f"📊 Testing R² Score: {test_score:.4f}")
print(f"📈 Model Coefficients:")
print(f"   - Light Intensity: {model.coef_[0]:.6f}")
print(f"   - Temperature: {model.coef_[1]:.6f}")
print(f"   - Intercept: {model.intercept_:.6f}")

# 4. Make Predictions
print("\n" + "-"*70)
print("⚡ MAKING POWER PREDICTIONS")
print("-"*70)

# Predict for different scenarios
test_cases = [
    ([800, 25], "Low Light, Moderate Temp"),
    ([2500, 32], "High Light, High Temp"),
    ([1500, 28], "Medium Light, Medium Temp"),
]

for light, temp in [(tc[0][0], tc[0][1]) for tc in test_cases]:
    prediction_data = pd.DataFrame([[light, temp]], columns=['light_intensity', 'temperature'])
    prediction = model.predict(prediction_data)[0]
    print(f"💡 Light: {light} lux, Temp: {temp}°C → Predicted Power: {prediction:.2f} W")

# 5. Anomaly Detection - Power Drop Analysis
print("\n" + "="*70)
print("⚠️  POWER OUTPUT ANOMALY DETECTION SYSTEM")
print("="*70)

# Get all power values in order
power_values = data['actual_power'].values
timestamps = data['timestamp'].values

anomaly_count = 0
critical_anomalies = []
major_anomalies = []
minor_anomalies = []

print("\n🔎 Scanning for power output decreases...\n")

for i in range(1, len(power_values)):
    prev_power = power_values[i-1]
    curr_power = power_values[i]
    
    # Only flag if current is lower and previous wasn't near zero
    if curr_power < prev_power and prev_power > 0.1:
        power_drop = prev_power - curr_power
        drop_percentage = (power_drop / prev_power) * 100
        
        anomaly_count += 1
        
        # Categorize by severity
        if drop_percentage >= 20:
            severity = "🔴 CRITICAL"
            critical_anomalies.append({
                'index': i,
                'timestamp': timestamps[i],
                'prev_power': prev_power,
                'curr_power': curr_power,
                'drop': power_drop,
                'percentage': drop_percentage
            })
        elif drop_percentage >= 10:
            severity = "🟠 MAJOR"
            major_anomalies.append({
                'index': i,
                'timestamp': timestamps[i],
                'prev_power': prev_power,
                'curr_power': curr_power,
                'drop': power_drop,
                'percentage': drop_percentage
            })
        else:
            severity = "🟡 MINOR"
            minor_anomalies.append({
                'index': i,
                'timestamp': timestamps[i],
                'prev_power': prev_power,
                'curr_power': curr_power,
                'drop': power_drop,
                'percentage': drop_percentage
            })
        
        if anomaly_count <= 10:  # Show first 10 anomalies
            print(f"{severity} Anomaly at Record {i} ({timestamps[i]}):")
            print(f"     Previous Power: {prev_power:.2f} W")
            print(f"     Current Power:  {curr_power:.2f} W")
            print(f"     Drop Amount:    {power_drop:.2f} W ({drop_percentage:.1f}%)")
            print()

# Summary Statistics
print("="*70)
print("📊 ANOMALY DETECTION SUMMARY")
print("="*70)
print(f"\n🔴 Critical Anomalies (≥20% drop):  {len(critical_anomalies)}")
print(f"🟠 Major Anomalies (10-20% drop):    {len(major_anomalies)}")
print(f"🟡 Minor Anomalies (<10% drop):      {len(minor_anomalies)}")
print(f"📈 Total Anomalies Detected:         {anomaly_count}")
print(f"✅ Healthy Records (no drop):        {len(power_values) - anomaly_count}")

# 6. User Notifications
print("\n" + "="*70)
print("📢 USER NOTIFICATIONS & RECOMMENDATIONS")
print("="*70)

if anomaly_count == 0:
    print("\n✅ NO ANOMALIES DETECTED")
    print("   Your solar panel is operating optimally with consistent power output!")
else:
    print(f"\n⚠️  {anomaly_count} ANOMALIES DETECTED")
    
    if critical_anomalies:
        print(f"\n🔴 URGENT ACTION REQUIRED!")
        print(f"   {len(critical_anomalies)} critical power drops detected (≥20%)")
        print("   Recommended Actions:")
        print("   - Check panel surface for dust/dirt accumulation")
        print("   - Inspect for shading or obstruction")
        print("   - Check temperature management and cooling")
        print("   - Verify electrical connections")

    if major_anomalies:
        print(f"\n🟠 ATTENTION NEEDED")
        print(f"   {len(major_anomalies)} major power drops detected (10-20%)")
        print("   Recommended Actions:")
        print("   - Clean panel surface if dust level is high")
        print("   - Monitor environmental conditions")
        print("   - Schedule maintenance inspection")

    if minor_anomalies:
        print(f"\n🟡 MONITORED")
        print(f"   {len(minor_anomalies)} minor power fluctuations detected (<10%)")
        print("   Status: Normal variations, continue monitoring")

# 7. Final Statistics
print("\n" + "="*70)
print("📈 OVERALL SYSTEM HEALTH")
print("="*70)

avg_power = y_clean.mean()
max_power = y_clean.max()
min_power = y_clean.min()
stability_score = (1 - (anomaly_count / len(power_values))) * 100

print(f"\n💡 Average Power Output:    {avg_power:.2f} W")
print(f"⚡ Maximum Power Output:    {max_power:.2f} W")
print(f"🔋 Minimum Power Output:    {min_power:.2f} W")
print(f"📊 System Stability Score:  {stability_score:.1f}%")

print("\n" + "="*70)
print("✅ ANALYSIS COMPLETE")
print("="*70 + "\n")
