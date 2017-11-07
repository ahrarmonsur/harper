/*
 ESP8266 Moisture by Ahrar Monsur
 Measures the moisture from a soil moisture sensor and uploads
 date to a webserver
*/

const int SENSOR_POWER = 15;
float vIn;

void setup() {
	pinMode(SENSOR_POWER, OUTPUT);     // Initialize the LED_BUILTIN pin as an output
	Serial.begin(115200);
}

// the loop function runs over and over again forever
void loop() {
//	digitalWrite(SENSOR_POWER, LOW);
//	delay(1000);
	digitalWrite(SENSOR_POWER, HIGH);  // Turn the LED off by making the voltage HIGH
	delay(1000);
	vIn = analogRead(A0);
	Serial.println(vIn);
	delay(1000);
	digitalWrite(SENSOR_POWER, LOW);  // Turn the LED off by making the voltage HIGH
	delay(2000);                      // Wait for two seconds (to demonstrate the active low LED)
}
