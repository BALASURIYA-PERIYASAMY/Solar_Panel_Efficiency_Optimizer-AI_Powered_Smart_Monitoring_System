import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("📊 BULK IMPORTING SOLAR DATA TO DATABASE")
print("="*70)

# 1. Connect to your MySQL Database
print("\n🔗 Connecting to MySQL database...")
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",        # Your MySQL username
        password="",        # Your MySQL password
        database="solar_optimizer"
    )
    cursor = db.cursor()
    print("✅ Connected to database successfully!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("   Make sure MySQL server is running and credentials are correct.")
    exit()

# 2. Train the AI Model (using the 1,000 rows we generated)
print("\n🤖 Training AI model...")
df = pd.read_csv(r'D:\Documents\Final Year Project\sample\solar_data_generated.csv', encoding='utf-8')
X = df[['light_intensity', 'temperature']]
y = df['actual_power']
model = LinearRegression().fit(X, y)
print(f"✅ Model trained with R² score: {model.score(X, y):.4f}")

# 3. Bulk Insert ALL data from CSV into database
print(f"\n📥 Preparing to insert {len(df)} records...")
sql = "INSERT INTO sensor_logs (timestamp, light_intensity, temperature, dust_level, actual_power, predicted_power, efficiency_gap) VALUES (%s, %s, %s, %s, %s, %s, %s)"

records_inserted = 0
errors_count = 0

for idx, row in df.iterrows():
    try:
        # Extract values from current row
        timestamp = row['timestamp']
        light_intensity = float(row['light_intensity'])
        temperature = float(row['temperature'])
        dust_level = float(row['dust_level'])
        actual_power = float(row['actual_power'])
        
        # AI Prediction
        predicted_power = float(model.predict([[light_intensity, temperature]])[0])
        efficiency_gap = predicted_power - actual_power
        
        # Insert into database
        val = (timestamp, light_intensity, temperature, dust_level, actual_power, predicted_power, efficiency_gap)
        cursor.execute(sql, val)
        records_inserted += 1
        
        # Show progress every 100 records
        if (idx + 1) % 100 == 0:
            print(f"   ✓ Processed {idx + 1}/{len(df)} records...")
    
    except Exception as e:
        errors_count += 1
        print(f"   ❌ Error at row {idx}: {e}")

# 4. Commit all changes
print("\n💾 Committing data to database...")
try:
    db.commit()
    print(f"✅ Successfully inserted {records_inserted} records!")
    if errors_count > 0:
        print(f"⚠️  {errors_count} records failed to insert")
except Exception as e:
    print(f"❌ Commit failed: {e}")

# 5. Display insertion summary
print("\n" + "="*70)
print("📊 INSERTION SUMMARY")
print("="*70)
print(f"📥 Total Records Inserted: {records_inserted}")
print(f"❌ Failed Records:         {errors_count}")
print(f"✅ Success Rate:           {(records_inserted/len(df)*100):.1f}%")

# 6. Verify data in database
print("\n🔍 Verifying data in database...")
try:
    cursor.execute("SELECT COUNT(*) FROM sensor_logs")
    total_records = cursor.fetchone()[0]
    print(f"✅ Total records in sensor_logs table: {total_records}")
    
    cursor.execute("SELECT AVG(actual_power) FROM sensor_logs")
    avg_power = cursor.fetchone()[0]
    print(f"💡 Average Power: {avg_power:.2f} W" if avg_power else "No data")
except Exception as e:
    print(f"❌ Verification failed: {e}")

# Close connection
cursor.close()
db.close()
print("\n" + "="*70)
print("✅ BULK IMPORT COMPLETE")
print("="*70 + "\n")

print(f"Data Saved! Gap: {efficiency_gap:.2f}W")