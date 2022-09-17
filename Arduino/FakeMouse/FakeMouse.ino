#include<HID-Project.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(2000000); //115200//250000//2000000
  Mouse.begin();
  //Keyboard.begin();
  //AbsoluteMouse.begin();
}

void loop() {
  if (Serial.available() > 0)
  {
     char in = Serial.read();
     char bray[3]; // was 3
     String sign;
     String dataString;
     
      if (in == 'X' || in == 'Y' || in == 'C' || in == 'U' || in == 'A'
          || in == 'B' || in == 'D' || in == 'E' || in == 'S'){ // || in == 'K'
        int count = 0;
        sign = in;
        while (true)
        {
          if (Serial.available() > 0)
          {
            bray[count] = Serial.read();
            if (bray[count] != 10){
              count ++;
              if (count >= 3){ // was 3
                String stri(bray);
                dataString = stri;
                break;
              }
            }
          }
        }
     //byte data = byte(in);
     //String strData = (String)data;

     //String sign = dataString.substring(0,1);
     //int x = dataString.substring(1,4).toInt(); //was 1 to 5
     int x = dataString.toInt(); //was 1 to 5
     int iterations = 0;
     //.println(x);
     if (x > 124){
        iterations = int(x / 124);
        x = x % 124;
     }

     if (sign == "C"){
           MoveMouse((-1*x),0);
           MoveMouseIteration(-120, 0, iterations);
     }
     else if (sign == "U"){
           MoveMouse(0,(-1*x));
           MoveMouseIteration(0, -120, iterations);
     }
     else if (sign == "X"){
           MoveMouse(x,0);
           MoveMouseIteration(120, 0, iterations);
     }
     else if (sign == "Y"){
           MoveMouse(0,x);
           MoveMouseIteration(0, 120, iterations);
     }
     else if (sign == "A"){
          Mouse.press();
     }
     else if (sign == "B"){
          Mouse.release();
     }
     else if (sign == "D"){
          Mouse.press(MOUSE_RIGHT);
     }
     else if (sign == "E"){
          Mouse.release(MOUSE_RIGHT);
     }
     /*else if (sign == "K"){
          switch(x) {
            case 0:
              Keyboard.press(KEY_UP);
              break;
            case 1:
              Keyboard.press(KEY_DOWN);
              break;
            case 2:
              Keyboard.press(KEY_LEFT);
              break;
            case 3:
              Keyboard.press(KEY_RIGHT);
              break;
            case 4:
              Keyboard.release(KEY_UP);
              break;
            case 5:
              Keyboard.release(KEY_DOWN);
              break;
            case 6:
              Keyboard.release(KEY_LEFT);
              break;
            case 7:
              Keyboard.release(KEY_RIGHT);
              break;
            default:
              break;
          }
     }*/
     else if (sign == "S"){
          delay(x);
     }
    }
  }
}

void MoveMouseIteration(int x, int y, int iteration){
  for (int i = 0; i < iteration; i++){
    MoveMouse(x, y);
  }
}

void MoveMouse(int x, int y){
  //if (x < 10 || y < 10){ //2
  //  scal = 0.75f;    
  //}
  //scal = 1.5f;    
  //else{
  //  scal = 0.98f;
  //}
  //else{
  //  scal = 1.2f;
  //}
  //int scal = 0.515f;
        //Mouse.move((x*scal),(y*scal));
        //Serial.print(x);
        Mouse.move(x,y);
        //delay(10);
}
