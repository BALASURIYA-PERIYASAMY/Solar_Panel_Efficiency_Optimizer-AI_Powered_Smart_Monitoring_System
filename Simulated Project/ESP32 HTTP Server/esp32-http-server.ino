/* ESP32 HTTP IoT Server Example for Wokwi.com

  https://wokwi.com/projects/320964045035274834

  To test, you need the Wokwi IoT Gateway, as explained here:

  https://docs.wokwi.com/guides/esp32-wifi#the-private-gateway

  Then start the simulation, and open http://localhost:9080
  in another browser tab.

  Note that the IoT Gateway requires a Wokwi Club subscription.
  To purchase a Wokwi Club subscription, go to https://wokwi.com/club
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <BH1750.h>

// Pin Definitions
#define POT_POWER_PIN 34   // Simulates Actual Solar Power (0-12W)
#define POT_DUST_PIN 32    // Simulates Dust accumulation
#define DHTPIN 4           // DHT22 Temperature Sensor
#define RELAY_PIN 5        // Cleaning Pump Relay
#define DHTTYPE DHT22

// Initialize Components
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;

void setup() {
  Serial.begin(115200);
  
  // Start Sensors
  Wire.begin(21, 22); // SDA, SCL
  dht.begin();
  lightMeter.begin();
  
  // Start LCD
  lcd.init();
  lcd.backlight();
  
  // Set Relay
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  lcd.print("AI Solar System");
  delay(2000);
  lcd.clear();
}

void loop() {
  // 1. Read Raw Sensor Data
  float temp = dht.readTemperature();
  float lux = lightMeter.readLightLevel();
  
  // 2. Simulate Actual Power from Potentiometer (0 to 12 Watts)
  int rawPower = analogRead(POT_POWER_PIN);
  float actualPower = (rawPower / 4095.0) * 12.0;

  // 3. Simple AI Prediction Logic (P = Light - Heat Loss)
  // In a real AI, these coefficients come from your Python training
  float predictedPower = (lux / 5000.0) * 10.0; 
  if (temp > 35) predictedPower -= (temp - 35) * 0.1; // Efficiency drop due to heat

  // 4. Maintenance Recommendation (The "Efficiency Gap")
  float gap = predictedPower - actualPower;
  bool needsCleaning = (gap > 1.5); // If gap > 1.5W, panel is likely dirty

  if (needsCleaning) {
    digitalWrite(RELAY_PIN, HIGH); // Turn on pump
  } else {
    digitalWrite(RELAY_PIN, LOW);
  }

  // 5. Update LCD Display
  lcd.setCursor(0, 0);
  lcd.print("Pwr:"); lcd.print(actualPower, 1); lcd.print("W ");
  lcd.print("T:"); lcd.print(temp, 0); lcd.print("C");

  lcd.setCursor(0, 1);
  if (needsCleaning) {
    lcd.print("STATUS: CLEANING");
  } else {
    lcd.print("STATUS: OPTIMAL ");
  }

  // 6. Serial Debugging for Dashboard
  Serial.print("Actual:"); Serial.print(actualPower);
  Serial.print(",Pred:"); Serial.print(predictedPower);
  Serial.print(",Lux:"); Serial.println(lux);

  delay(2000); // Read every 2 seconds
}