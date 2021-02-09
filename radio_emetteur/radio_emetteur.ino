
#include <SoftwareSerial.h>
// Ceci est un test de communication radio avec processing

static const int RXPin = 2, TXPin = 3;
static const uint32_t RadioBaud = 9600;
int i;

SoftwareSerial ss(RXPin, TXPin);

void setup() {
  // put your setup code here, to run once:
  ss.begin(RadioBaud);
  Serial.begin(9600);
  pinMode(13, OUTPUT);
}
void loop() {
  // put your main code here, to run repeatedly:
  float r = random()*3;
  //Serial.println(i);
  //Serial.println(r);
  ss.println(i);
  ss.println(r);
  digitalWrite(13, HIGH);
  delay(500);
  digitalWrite(13, LOW);  
  delay(500);
  i = i + 1;
}
