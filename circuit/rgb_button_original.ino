void setup() {
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(2, INPUT_PULLUP);  // button: pin 2 to GND
}

// Waits until the button is pressed, then released.
void waitForPress() {
  while (digitalRead(2) == HIGH) {}
  delay(50);
  while (digitalRead(2) == LOW) {}
  delay(50);
}

void loop() {
  waitForPress();
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 255);
  delay(500);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);

  waitForPress();
  analogWrite(9, 0);
  analogWrite(10, 127);
  analogWrite(11, 255);
  delay(500);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);

  waitForPress();
  analogWrite(9, 0);
  analogWrite(10, 255);
  analogWrite(11, 255);
  delay(500);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);

  waitForPress();
  analogWrite(9, 0);
  analogWrite(10, 255);
  analogWrite(11, 0);
  delay(500);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);

  waitForPress();
  analogWrite(9, 255);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);

  waitForPress();
  analogWrite(9, 130);
  analogWrite(10, 0);
  analogWrite(11, 75);
  delay(500);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);

  waitForPress();
  analogWrite(9, 211);
  analogWrite(10, 0);
  analogWrite(11, 148);
  delay(500);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  delay(500);
}
