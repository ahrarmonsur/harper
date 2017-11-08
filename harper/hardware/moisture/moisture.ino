/*
 ESP8266 Moisture by Ahrar Monsur
 Measures the moisture from a soil moisture sensor and uploads
 date to a webserver
*/


#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>

const char* ssid     = "Ahrar987";
const char* password = "mon987syeda";

const char* host = "http://harper.thehumanmachine.link/moisture";
const char* streamId   = "....................";
const char* privateKey = "....................";

const int SENSOR_POWER = 15;
int vIn;

ESP8266WiFiMulti WiFiMulti;



void setup() {
	pinMode(SENSOR_POWER, OUTPUT);     // Initialize the LED_BUILTIN pin as an output
	Serial.begin(115200);
	delay(10);

	// Connect to WiFi network
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

	// Countdown to WiFi connection
	for(uint8_t t = 4; t > 0; t--) {
        Serial.printf("[SETUP] WAIT %d...\n", t);
        Serial.flush();
        delay(1000);
    }

	// Set Wifi to station mode
	WiFi.mode(WIFI_STA);
	WiFiMulti.addAP(ssid, password);

	// Print Wifi connection details
    if(WiFiMulti.run() == WL_CONNECTED) {
		Serial.println("");
		Serial.println("WiFi connected");
		Serial.println("IP address: ");
		Serial.println(WiFi.localIP());
	}

}

void loop() {
//	digitalWrite(SENSOR_POWER, LOW);:w
//	delay(1000);
    if(WiFiMulti.run() == WL_CONNECTED) {
		digitalWrite(SENSOR_POWER, HIGH);  // Turn the LED off by making the voltage HIGH
		delay(1000);
		vIn = analogRead(A0);
		Serial.println(vIn);
		delay(1000);
		digitalWrite(SENSOR_POWER, LOW);  // Turn the LED off by making the voltage HIGH
		delay(2000);                      // Wait for two seconds (to demonstrate the active low LED)

		HTTPClient http;
		Serial.println("[HTTP] begin...");
		http.begin(host);
		http.addHeader("Content-Type", "application/x-www-form-urlencoded");
		String payload = "measurement=";
		int httpCode = http.POST(payload + vIn);
		Serial.println(httpCode);
		Serial.println(payload+vIn);
		if(httpCode > 0) {
			Serial.printf("[HTTP] POST... code: %d\n", httpCode);
			if(httpCode == HTTP_CODE_OK) {
				String payload = http.getString();
				Serial.println(payload);
			}
		} else {
			Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
		}
		http.end();
	} else {
		Serial.println("Could not connect to Wifi.");
	}
	delay(3000);
}
