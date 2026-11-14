# LED + Button circuit (Tinkercad Circuits)

Pressing the button toggles the LED. Build it in Tinkercad Circuits (Circuits > Create new Circuit).

## Parts
- 1x Arduino Uno R3
- 1x LED (red)
- 1x 220 ohm resistor
- 1x pushbutton
- 1x breadboard + jumper wires

## Wiring
| From | To |
|---|---|
| Arduino pin 8 | 220 ohm resistor, one leg |
| Resistor other leg | LED anode (long leg) |
| LED cathode (short leg) | Arduino GND |
| Arduino pin 2 | Pushbutton, one side |
| Pushbutton other side | Arduino GND |

The button uses the internal pull-up resistor, so no external resistor is needed.

## Code
Click "Code" > switch to Text, paste `led_button.ino`, then Start Simulation.
