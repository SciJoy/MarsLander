#include <Servo.h>

//Setting up pins on the Arduino
int azimuthGauge = 5;
int elevationGauge = 6;
int panServo = 8;
int tiltServo = 9;
int up = 10;
int down = 11;
int left = 12;
int right = 13;
int restart = 2; //signal from Pi to reset to anntenna for next team
int antennaLock = 7; //signal to Pi to say the anntenna is in the right place

//Setting up varbiables
int azimuthPos = 0;
int elevationPos =0;
int panPos = 10;
int tiltPos = 10;
int jogSpeed = 5;
int azimuthInitial = 10;
int elevationInitial = 10;
int panInitial = 10;
int tiltInitial = 10;
int gaugeMin = 0;
int gaugeMax = 190;
int servoMax = 160;
int servoMin = 10;
int desiredAzimuth = 140;
int desiredElevation = 140;

//Initiating servo class
Servo pan;
Servo tilt;

void setup() {
  //Setting up pins
  pinMode(up, INPUT);
  pinMode(down, INPUT);
  pinMode(left, INPUT);
  pinMode(right, INPUT);
  pinMode(restart, INPUT);
  pinMode(antennaLock, OUTPUT);
  pinMode(azimuthGauge, OUTPUT);
  pinMode(elevationGauge, OUTPUT);

  //Attaching servos and setting initial position
  pan.attach(panServo);
  tilt.attach(tiltServo);
  pan.write(panInitial);
  delay(50);
  tilt.write(tiltInitial);
  delay(50);
  analogWrite(azimuthGauge,azimuthInitial);
  analogWrite(elevationGauge,elevationInitial);

  azimuthPos = azimuthInitial;
  elevationPos = elevationInitial;

  //Start serial monitor
  Serial.begin(9600);
  Serial.println("The start");
}

void loop() {

  if(digitalRead(restart) == HIGH){
    Serial.println("Resetting");
    pan.write(panInitial);
    delay(500);
    tilt.write(tiltInitial);
    delay(500);
    analogWrite(azimuthGauge,azimuthInitial);
    analogWrite(elevationGauge,elevationInitial);
   }

 //right-pan-azimuth
  if(digitalRead(right) == HIGH && azimuthPos <= servoMax){
    Serial.println("Right");

    //Move elevation gauge
    azimuthPos = azimuthPos + jogSpeed;
    Serial.println(azimuthPos);
    analogWrite(azimuthGauge,azimuthPos);

    //Move pan servo
    panPos = panPos + jogSpeed;
    pan.write(panPos);
    delay(500);
    Serial.print("pos right: ");
    Serial.println(panPos);

      if(desiredAzimuth == azimuthPos){
       Serial.println("postition locked");
       digitalWrite(antennaLock, HIGH);
      }

   }


 //left-pan-azimuth
  if(digitalRead(left) == HIGH && azimuthPos >= servoMin){
    Serial.println("Left");

    //Move elevation gauge
    azimuthPos = azimuthPos - jogSpeed;
    Serial.println(azimuthPos);
    analogWrite(azimuthGauge,azimuthPos);

    //Move pan servo
    panPos = panPos - jogSpeed;
    pan.write(panPos);
    delay(500);
    Serial.print("pos right: ");
    Serial.println(panPos);

      if(desiredAzimuth == azimuthPos && desiredElevation == elevationPos){
       Serial.println("postition locked");
       digitalWrite(antennaLock, HIGH);
      }

   }

//up-tilt-elevation
  if(digitalRead(up) == HIGH && elevationPos <= servoMax){
    Serial.println("up");

    //Move elevation gauge
    elevationPos = elevationPos + jogSpeed;
    Serial.println(elevationPos);
    analogWrite(elevationGauge,elevationPos);

    //Move pan servo
    tiltPos = tiltPos + jogSpeed;
    tilt.write(tiltPos);
    delay(500);
    Serial.print("pos up: ");
    Serial.println(tiltPos);

      if(desiredAzimuth == azimuthPos && desiredElevation == elevationPos){
       Serial.println("postition locked");
       digitalWrite(antennaLock, HIGH);
      }

   }

//down-tilt-elevation
  if(digitalRead(down) == HIGH && elevationPos >= servoMin){
    Serial.println("Down");

    //Move elevation gauge
    elevationPos = elevationPos - jogSpeed;
    Serial.println(elevationPos);
    analogWrite(elevationGauge,elevationPos);

    //Move pan servo
    tiltPos = tiltPos - jogSpeed;
    tilt.write(tiltPos);
    delay(500);
    Serial.print("pos up: ");
    Serial.println(tiltPos);

      if(desiredAzimuth == azimuthPos && desiredElevation == elevationPos){
       Serial.println("postition locked");
       digitalWrite(antennaLock, HIGH);
      }

   }

Serial.println("End of loop: ");
delay(1000);

}
