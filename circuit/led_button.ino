const int LED_PIN = 8;
const int BUTTON_PIN = 2;

bool ledOn = false;
bool lastState = HIGH;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  bool state = digitalRead(BUTTON_PIN);
  if (lastState == HIGH && state == LOW) {
    ledOn = !ledOn;
    digitalWrite(LED_PIN, ledOn);
    delay(50); // debounce
  }
  lastState = state;
}
