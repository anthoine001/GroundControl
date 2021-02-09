#include <SoftwareSerial.h>
// Ceci est un test de communication radio avec processing

static const int RXPin = 2, TXPin = 3;
static const uint32_t RadioBaud = 9600;


SoftwareSerial ss(RXPin, TXPin);

void setup() {
  // put your setup code here, to run once:
  ss.begin(RadioBaud);
  Serial.begin(9600);
  Serial.println("demarrage");
}
void loop() {
  // put your main code here, to run repeatedly:
  if(ss.available()>0){
    Serial.println(ss.readStringUntil('\n'));
     
  }
}
