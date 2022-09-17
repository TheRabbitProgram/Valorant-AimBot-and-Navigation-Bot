#include<HID-Project.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(2000000); //115200//250000//2000000
  Keyboard.begin();
  //AbsoluteMouse.begin();
}

void loop() {
  if (Serial.available() > 0)
  {
     char in = Serial.read();
          switch(in) {
            case 'A':
              Keyboard.press(KEY_UP);
              break;
            case 'B':
              Keyboard.press(KEY_DOWN);
              break;
            case 'C':
              Keyboard.press(KEY_LEFT);
              break;
            case 'D':
              Keyboard.press(KEY_RIGHT);
              break;
            case 'E':
              Keyboard.press('p');
              break;
            case 'F':
              Keyboard.press('o');
              break;
            case 'G':
              Keyboard.release(KEY_UP);
              break;
            case 'H':
              Keyboard.release(KEY_DOWN);
              break;
            case 'I':
              Keyboard.release(KEY_LEFT);
              break;
            case 'J':
              Keyboard.release(KEY_RIGHT);
              break;
            case 'K':
              Keyboard.release('p');
              break;
            case 'L':
              Keyboard.release('o');
              break;
            default:
              break;
          }
  }
}
