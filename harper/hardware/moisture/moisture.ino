/*
 ESP8266 Moisture by Ahrar Monsur
 Measures the moisture from a soil moisture sensor and uploads
 date to a webserver
*/


#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include "secrets.h"

const String SERVER_ADDRESS = "http://harper.thehumanmachine.link";
const int RELAY_PIN = 12;
const int SENSOR_POWER = 15;
const int TURBO_PIN = 13;

const bool UPLOAD_DATA = true;
int moistureValue;
int turboPressed;
int permissionToMeasure;

int aridityThreshold = 900;			// The value from the sensor, above which the watering routine will be triggered
int cadence = 3600000;				// The number of milliseconds between regular readings
//int cadence = 5000;					// The number of milliseconds between regular readings
int turboCadence = 500;				// The number of milliseconds between regular readings with turbo button pressed
int wateringDuration = 4000;
unsigned long msSinceMeasurement;

ESP8266WiFiMulti WiFiMulti;



void setup() {
	pinMode(SENSOR_POWER, OUTPUT);
	pinMode(TURBO_PIN, INPUT);
	pinMode(RELAY_PIN, OUTPUT);
	Serial.begin(115200);
	delay(10);

	setRelayState(0);

	// Connect to WiFi network
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ROUTER_SSID);

	// Countdown to WiFi connection
	for (uint8_t t = 4; t > 0; t--) {
        Serial.printf("[SETUP] WAIT %d...\n", t);
        Serial.flush();
        delay(1000);
    }

	// Set Wifi to station mode
	WiFi.mode(WIFI_STA);
	WiFiMulti.addAP(ROUTER_SSID, ROUTER_PASSWORD);

	// Print Wifi connection details
    if (WiFiMulti.run() == WL_CONNECTED) {
		Serial.println("");
		Serial.println("WiFi connected");
		Serial.println("IP address: ");
		Serial.println(WiFi.localIP());
	} else {
		Serial.println("CONNECTION FAILED");
	}
	// Give permission to measure
	permissionToMeasure = 1;

}

void loop() {
	turboPressed = digitalRead(TURBO_PIN);
	if ((millis() - msSinceMeasurement) > (turboPressed ? turboCadence : cadence)) {
		permissionToMeasure = 1;
	}
    if (permissionToMeasure) {
    	moistureValue = readSensor();
		permissionToMeasure = 0;
		msSinceMeasurement = millis();

    	if (UPLOAD_DATA) {
    		if (WiFiMulti.run() == WL_CONNECTED) {
				String fieldName = "measurement=";
				String payload = fieldName + moistureValue;
				String url = SERVER_ADDRESS + "/moisture";
				sendPostRequest(url, payload);
			} else {
				Serial.println("Attempting to reconnect to Wifi...");
				WiFiMulti.addAP(ROUTER_SSID, ROUTER_PASSWORD);
			}
		}

		if (moistureValue >= aridityThreshold) {
			waterPlant();
		}
	}
}

int readSensor() {
	int measurement;

	digitalWrite(SENSOR_POWER, HIGH);			// Supply power to sensor
	delay(500);									// Wait for circuit to energize
	measurement = analogRead(A0);				// Read the measurement from the sensor
	Serial.println(measurement);
	digitalWrite(SENSOR_POWER, LOW);			// Turn off power to the sensor; this reduces the effects of corrosion
	delay(500);									// Wait for circuit to energize
	return measurement;
}

void setRelayState(int relayOn) {
	// The relay is active low
	if (relayOn) {
		digitalWrite(RELAY_PIN, LOW);
	} else {
		digitalWrite(RELAY_PIN, HIGH);
	}
}

void waterPlant() {
	unsigned long msBegin, duration;

	msBegin = millis();
	setRelayState(1);
	delay(wateringDuration);
	setRelayState(0);
	duration = millis() - msBegin;

	String payload = "plantName=Paddles&type=submersiblePump_120lph&duration=";
	payload = payload + duration;
	String url = SERVER_ADDRESS + "/moisture/irrigation";
	sendPostRequest(url, payload);
}

void sendPostRequest(String url, String payload) {
	HTTPClient http;
	Serial.println("[HTTP] begin...");
	http.begin(url);
	http.addHeader("Content-Type", "application/x-www-form-urlencoded");
	int httpCode = http.POST(payload);
	Serial.println(payload);
	if (httpCode > 0) {
		Serial.printf("[HTTP] POST... code: %d\n", httpCode);
	} else {
		Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
	}
	http.end();
}
