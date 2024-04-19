int sensorValue;
int sensorLow = 380;
int sensorHigh = 620;

void setup() {
  Serial.begin(9600);
  pinMode(9, OUTPUT); // Nastavíme vstavanú LED ako výstup
}

void loop() {
  sensorValue = analogRead(A0);
  Serial.println(sensorValue);
  
  // Inverzne mapovanie hodnôt zo senzora na rozsah PWM (255-0)
  int brightness = map(sensorValue, sensorLow, sensorHigh, 255, 0);
  Serial.println(brightness);
  // Nastavíme intenzitu svietenia vstavanej LED
  analogWrite(9, brightness);
  
  delay(10);
}
