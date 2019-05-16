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
int restart = 7; //signal from Pi to reset to anntenna for next team
int antennaLock = 2; //signal to Pi to say the anntenna is in the right place

//Tracking varbiables
int azimuthPos = 0;
int elevationPos =0;
int panPos = 0;
int tiltPos = 0;

//Initialize
int jogSpeed = 5; //what the incremental movement is
int azimuthInitial = 10;
int elevationInitial = 10;
int panInitial = 10;
int tiltInitial = 10;

//Limits and desired
int gaugeMin = 0;
int gaugeMax = 190;
int servoMax = 160;
int servoMin = 10;
int desiredAzimuthMax = 140;
int desiredElevationMax = 140;
int desiredAzimuthMin = 120;
int desiredElevationMin = 120;

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
  panPos = panInitial;
  tiltPos = tiltInitial;
  
  azimuthPos = azimuthInitial;
  elevationPos = elevationInitial;
  
  //Start serial monitor
  Serial.begin(9600);
  Serial.println("The start");
}

void loop() {
  
  if(digitalRead(restart) == HIGH){
    Serial.println("Resetting");
    //Reset servos and gauges
    pan.write(panInitial);
    delay(500);
    tilt.write(tiltInitial);
    delay(500);
    analogWrite(azimuthGauge,azimuthInitial);
    analogWrite(elevationGauge,elevationInitial); 
    //Reset postions
    panPos = panInitial;
    tiltPos = tiltInitial;
    azimuthPos = azimuthInitial;
    elevationPos = elevationInitial;
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

    //If both gauges are lined up, then send signal to the Pi
    if(azimuthPos <= desiredAzimuthMax && azimuthPos >= desiredAzimuthMin && elevationPos <= desiredElevationMax && elevationPos >= desiredElevationMin){
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


    //If both gauges are lined up, then send signal to the Pi
    if(azimuthPos <= desiredAzimuthMax && azimuthPos >= desiredAzimuthMin && elevationPos <= desiredElevationMax && elevationPos >= desiredElevationMin){
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

    
    //If both gauges are lined up, then send signal to the Pi
    if(azimuthPos <= desiredAzimuthMax && azimuthPos >= desiredAzimuthMin && elevationPos <= desiredElevationMax && elevationPos >= desiredElevationMin){
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

    //If both gauges are lined up, then send signal to the Pi
    if(azimuthPos <= desiredAzimuthMax && azimuthPos >= desiredAzimuthMin && elevationPos <= desiredElevationMax && elevationPos >= desiredElevationMin){
     Serial.println("postition locked");
     digitalWrite(antennaLock, HIGH); 
    }
    
   }

//Delay so they can look at the gauges
delay(1000);

}

