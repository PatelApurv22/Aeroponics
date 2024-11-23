#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <SD.h>
#include <Wire.h>
#include <RTClib.h>
#include <LiquidCrystal_I2C.h>

// Pin Definitions
#define DHTPIN 2
#define DHTTYPE DHT11
#define MQ2PIN A0
#define TRIGPIN 3
#define ECHOPIN 4
#define BUZZERPIN 8
#define RELAYPIN1 7
#define RELAYPIN2 6
#define WATER_TEMP_PIN 5
#define CSPIN 10
#define BUTTONPIN 9

// Sensor and Module Objects
DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(WATER_TEMP_PIN);
DallasTemperature sensors(&oneWire);
RTC_DS3231 rtc;
LiquidCrystal_I2C lcd(0x27, 16, 2);

unsigned long lastSerialTime = 0;
const unsigned long serialInterval = 2000;
int gasThreshold = 800;  // Default gas threshold
float waterLevelThreshold = 10.0; // Default water level threshold

void setup() {
  Serial.begin(9600);
  dht.begin();
  sensors.begin();
  lcd.init();
  lcd.backlight();

  // RTC Initialization
  if (!rtc.begin()) {
    Serial.println("RTC not found!");
    while (1);
  }
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  // Pin Modes
  pinMode(MQ2PIN, INPUT);
  pinMode(TRIGPIN, OUTPUT);
  pinMode(ECHOPIN, INPUT);
  pinMode(BUZZERPIN, OUTPUT);
  pinMode(RELAYPIN1, OUTPUT);
  pinMode(RELAYPIN2, OUTPUT);
  pinMode(BUTTONPIN, INPUT_PULLUP);

  // SD Card Initialization
  if (!SD.begin(CSPIN)) {
    Serial.println("SD Card initialization failed!");
    while (1);
  }
  Serial.println("SD Card initialized.");
}

void loop() {
  // Read DHT11
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Check DHT sensor
  if (isnan(h) || isnan(t)) {
    Serial.println("Error reading DHT sensor!");
    logError("DHT Sensor Error");
    return;
  }

  // Read DS18B20
  sensors.requestTemperatures();
  float waterTemp = sensors.getTempCByIndex(0);
  if (waterTemp == DEVICE_DISCONNECTED_C) {
    Serial.println("Error reading water temperature!");
    logError("Water Temp Sensor Error");
    return;
  }

  // Read MQ2
  int gasLevel = analogRead(MQ2PIN);

  // Measure Water Level
  digitalWrite(TRIGPIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGPIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGPIN, LOW);
  float duration = pulseIn(ECHOPIN, HIGH);
  float distance = duration * 0.034 / 2;

  // Get Current Time
  DateTime now = rtc.now();

  // Gas Level Check
  if (gasLevel > gasThreshold) {
    digitalWrite(BUZZERPIN, HIGH);
    lcd.setCursor(0, 0);
    lcd.print("Gas Alert!");
    Serial.println("Warning: High gas level detected!");
  } else {
    digitalWrite(BUZZERPIN, LOW);
  }

  // Water Level Check
  if (distance > waterLevelThreshold) {
    digitalWrite(BUZZERPIN, HIGH);
    lcd.setCursor(0, 1);
    lcd.print("Low Water!");
    Serial.println("Warning: Low water level!");
  } else {
    digitalWrite(BUZZERPIN, LOW);
  }

  // Manual Pump Control
  if (digitalRead(BUTTONPIN) == LOW) {
    digitalWrite(RELAYPIN1, HIGH);
    delay(10000);  // Run pump for 10 seconds
    digitalWrite(RELAYPIN1, LOW);
  }

  // Automated Pump Control
  if (now.hour() % 12 == 0 && now.minute() == 0 && now.second() == 0) {
    digitalWrite(RELAYPIN1, HIGH);
    delay(60000);
    digitalWrite(RELAYPIN1, LOW);
  }

  // Log Data to SD Card
  logData(now, t, h, waterTemp, gasLevel, distance);

  // Display Data on LCD
  lcd.setCursor(0, 0);
  lcd.print("Air:");
  lcd.print(t);
  lcd.print("C ");
  lcd.print("Hum:");
  lcd.print(h);
  lcd.print("%");
  lcd.setCursor(0, 1);
  lcd.print("Water:");
  lcd.print(waterTemp);
  lcd.print("C ");

  // Display Data on Serial Monitor
  unsigned long currentMillis = millis();
  if (currentMillis - lastSerialTime >= serialInterval) {
    lastSerialTime = currentMillis;
    Serial.print("Timestamp: ");
    Serial.print(now.timestamp());
    Serial.print(" | Air Temp: ");
    Serial.print(t);
    Serial.print("C | Humidity: ");
    Serial.print(h);
    Serial.print("% | Water Temp: ");
    Serial.print(waterTemp);
    Serial.print("C | Gas Level: ");
    Serial.print(gasLevel);
    Serial.print(" | Water Level: ");
    Serial.print(distance);
    Serial.println(" cm");
  }

  delay(1000);
}

void logData(DateTime now, float t, float h, float waterTemp, int gasLevel, float distance) {
  File dataFile = SD.open("data.csv", FILE_WRITE);
  if (dataFile) {
    if (dataFile.size() == 0) {
      dataFile.println("Timestamp,AirTemp(C),Humidity(%),WaterTemp(C),GasLevel,WaterLevel(cm)");
    }
    dataFile.print(now.timestamp());
    dataFile.print(",");
    dataFile.print(t);
    dataFile.print(",");
    dataFile.print(h);
    dataFile.print(",");
    dataFile.print(waterTemp);
    dataFile.print(",");
    dataFile.print(gasLevel);
    dataFile.print(",");
    dataFile.println(distance);
    dataFile.close();
  } else {
    Serial.println("Error writing to SD card.");
  }
}

void logError(String error) {
  File errorFile = SD.open("error.log", FILE_WRITE);
  if (errorFile) {
    DateTime now = rtc.now();
    errorFile.print(now.timestamp());
    errorFile.print(" - ");
    errorFile.println(error);
    errorFile.close();
  }
}
