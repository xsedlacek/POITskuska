int sensorValue;
int sensorLow = 0;
int sensorHigh = 500;
bool manual = false;
void setup() {
  Serial.begin(9600);
  pinMode(9, OUTPUT);// Nastavíme vstavanú LED ako výstup
  pinMode(A5, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();
    if(receivedChar == '1'){
      manual = true;
      }
    else{
      manual = false;
      }
  }
  if(manual){
    
    }
  else{
    sensorValue = analogRead(A5);
    
  
    // Inverzne mapovanie hodnôt zo senzora na rozsah PWM (255-0)
    int brightness = map(sensorValue, sensorLow, sensorHigh, 255, 0);
    // Nastavíme intenzitu svietenia vstavanej LED
    Serial.println(sensorValue);
    analogWrite(9, 255-brightness);
  }
  
  
  delay(2000);
}
