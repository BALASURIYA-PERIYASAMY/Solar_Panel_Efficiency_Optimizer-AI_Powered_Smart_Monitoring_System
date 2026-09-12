import mysql.connector
import time

def check_efficiency():
    db = mysql.connector.connect(host="localhost", user="root", password="", database="solar_optimizer")
    cursor = db.cursor()

    while True:
        # 1. Fetch the latest record from your MySQL table
        cursor.execute("SELECT efficiency_gap, dust_level FROM sensor_logs ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        if result:
            gap, dust = result
            print(f"Current Gap: {gap}W | Dust Level: {dust}")

            # 2. Decision Logic
            if gap > 1.5 or dust > 0.5: # Adjust these numbers based on your panel size
                print("⚠️ ALERT: Efficiency Low! Triggering Cleaning System...")
                # Here we would call a function to tell the ESP32 to turn on the relay
                # trigger_esp32_pump()
            else:
                print("✅ System Optimized.")

        time.sleep(10) # Check every 10 seconds

check_efficiency()