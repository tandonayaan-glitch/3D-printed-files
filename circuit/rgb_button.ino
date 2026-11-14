// RGB LED rainbow: each button press advances to the next colour.
// Button: pin 2 -> button -> GND (internal pull-up, no resistor needed).

const int R_PIN = 9;
const int G_PIN = 10;
const int B_PIN = 11;
const int BUTTON_PIN = 2;

// Same colours as the original sketch (R, G, B), plus off at the start.
const int colors[][3] = {
  {0,   0,   255},  // blue
  {0,   127, 255},  // light blue
  {0,   255, 255},  // cyan
  {0,   255, 0},    // green
  {255, 0,   0},    // red
  {130, 0,   75},   // indigo
  {211, 0,   148},  // violet
};
const int NUM_COLORS = sizeof(colors) / sizeof(colors[0]);

int index = -1;  // -1 = off until first press
bool lastState = HIGH;

void show(int i) {
  if (i < 0) {
    analogWrite(R_PIN, 0);
    analogWrite(G_PIN, 0);
    analogWrite(B_PIN, 0);
  } else {
    analogWrite(R_PIN, colors[i][0]);
    analogWrite(G_PIN, colors[i][1]);
    analogWrite(B_PIN, colors[i][2]);
  }
}

void setup() {
  pinMode(R_PIN, OUTPUT);
  pinMode(G_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  show(-1);
}

void loop() {
  bool state = digitalRead(BUTTON_PIN);
  if (lastState == HIGH && state == LOW) {
    index = (index + 1) % NUM_COLORS;
    show(index);
    delay(50);  // debounce
  }
  lastState = state;
}
