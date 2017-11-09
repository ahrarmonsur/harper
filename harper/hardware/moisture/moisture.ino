/*
 ESP8266 Moisture by Ahrar Monsur
 Measures the moisture from a soil moisture sensor and uploads
 date to a webserver
*/


#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>

const char* SSID     = "Ahrar987";
const char* PASSWORD = "mon987syeda";

const char* HOST = "http://harper.thehumanmachine.link/moisture";

const int SENSOR_POWER = 15;
const int TURBO_PIN = 13;
int moistureValue;
int turboPressed;
int permissionToMeasure;
int cadence = 3600000;					// The number of milliseconds between regular readings
int turboCadence = 500;					// The number of milliseconds between regular readings with turbo button pressed
unsigned long msSinceMeasurement;

ESP8266WiFiMulti WiFiMulti;



void setup() {
	pinMode(SENSOR_POWER, OUTPUT);     // Initialize the LED_BUILTIN pin as an output
	pinMode(TURBO_PIN, INPUT);     // Initialize the LED_BUILTIN pin as an output
	Serial.begin(115200);
	delay(10);

	// Connect to WiFi network
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(SSID);

	// Countdown to WiFi connection
	for (uint8_t t = 4; t > 0; t--) {
        Serial.printf("[SETUP] WAIT %d...\n", t);
        Serial.flush();
        delay(1000);
    }

	// Set Wifi to station mode
	WiFi.mode(WIFI_STA);
	WiFiMulti.addAP(SSID, PASSWORD);

	// Print Wifi connection details
    if (WiFiMulti.run() == WL_CONNECTED) {
		Serial.println("");
		Serial.println("WiFi connected");
		Serial.println("IP address: ");
		Serial.println(WiFi.localIP());
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
    	if (WiFiMulti.run() == WL_CONNECTED) {
			digitalWrite(SENSOR_POWER, HIGH);
			delay(1000);
			moistureValue = analogRead(A0);
			Serial.println(moistureValue);
			digitalWrite(SENSOR_POWER, LOW);

			String fieldName = "measurement=";
			String payload = fieldName + moistureValue;
			sendHTTPPost( payload);
			permissionToMeasure = 0;
			msSinceMeasurement = millis();
		} else {
			Serial.println("Could not connect to Wifi.");
		}
	}
}

void sendHTTPPost(String payload) {
	HTTPClient http;
	Serial.println("[HTTP] begin...");
	http.begin(HOST);
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
