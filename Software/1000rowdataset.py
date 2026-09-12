import pandas as pd
import numpy as np
import datetime
import os

# 1. Configuration
num_rows = 1000
start_time = datetime.datetime(2026, 2, 1, 6, 0) # Start at 6 AM
output_file = 'solar_data_generated.csv'

# 2. Generate Synthetic Data
data = []
for i in range(num_rows):
    current_time = start_time + datetime.timedelta(minutes=15 * i)
    hour = current_time.hour
    
    # Simulate Sunlight (Sine wave logic: peaks at noon, 0 at night)
    if 6 <= hour <= 18:
        light_intensity = int(3500 * np.sin(np.pi * (hour - 6) / 12) + np.random.normal(0, 50))
    else:
        light_intensity = np.random.randint(0, 10) # Moonlight/Night
    
    # Simulate Temperature (rises with sunlight)
    temp = 22 + (light_intensity / 150) + np.random.normal(0, 0.5)
    
    # Simulate Dust Accumulation (gradual increase over days)
    dust_level = 0.05 + (i * 0.0008) + np.random.normal(0, 0.01)
    
    # Calculate Power (Physics-based logic: Power = Light * Efficiency)
    # Efficiency drops if Temp > 25 or Dust > 0.3
    base_efficiency = 0.002 # Scaling for a 5W-10W panel
    temp_loss = max(0, (temp - 25) * 0.02) 
    dust_loss = max(0, (dust_level - 0.3) * 1.5)
    
    actual_power = (light_intensity * base_efficiency) - temp_loss - dust_loss
    actual_power = max(0, round(actual_power, 2)) # Cannot be negative

    data.append([current_time.strftime("%Y-%m-%d %H:%M"), light_intensity, round(temp, 1), round(dust_level, 3), actual_power])

# 3. Save to CSV
df = pd.DataFrame(data, columns=['timestamp', 'light_intensity', 'temperature', 'dust_level', 'actual_power'])

# Try to remove old file, if locked rename it instead
if os.path.exists(output_file):
    try:
        os.remove(output_file)
    except PermissionError:
        # If locked, rename the old file
        old_backup = output_file.replace('.csv', '_old.csv')
        try:
            if os.path.exists(old_backup):
                os.remove(old_backup)
            os.rename(output_file, old_backup)
        except:
            pass

df.to_csv(output_file, index=False)
print(f"✅ Success! '{output_file}' with 1,000 rows has been created.")