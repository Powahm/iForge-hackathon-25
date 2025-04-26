#include <SparkFun_TB6612.h>
#include <Servo.h>

// Pins for all inputs, keep in mind the PWM defines must be on PWM pins
// the default pins listed are the ones used on the Redbot (ROB-12097) with
// the exception of STBY which the Redbot controls with a physical switch
#define AIN1 2
#define BIN1 7
#define AIN2 4
#define BIN2 8
#define PWMA 3
#define PWMB 6
#define STBY 9

// these constants are used to allow you to make your motor configuration 
// line up with function names like forward.  Value can be 1 or -1
const int offsetA = 1;
const int offsetB = 1;

// Initializing motors.  The library will allow you to initialize as many
// motors as you have memory for.  If you are using functions like forward
// that take 2 motors as arguements you can either write new functions or
// call the function more than once.
Motor motor1 = Motor(AIN1, AIN2, PWMA, offsetA, STBY);
Motor motor2 = Motor(BIN1, BIN2, PWMB, offsetB, STBY);

const int servoPin = 11;
Servo fanServo;

int fanSpeed = 10;
int servoAngle = 90; // Center position
bool sweeping = false; // Sweep mode flag
int sweepDirection = 1; // 1 = right, -1 = left

unsigned long lastSweepTime = 0;
const int sweepDelay = 30; // ms delay between servo moves
const int sweepMin = 30; // Min angle for sweeping (not full left)
const int sweepMax = 150; // Max angle for sweeping (not full right)

void setup() {

  // Attach the servo
  fanServo.attach(servoPin);

  // Initialize
  stopFan();
  fanServo.write(servoAngle);

  // Start serial for voice command input
  Serial.begin(9600);
  Serial.println("Voice Controlled Fan Ready...");
}

void loop() {
  // Check for serial input
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Clean whitespace

    // Interpret command
    if (command.equalsIgnoreCase("fan on")) {
      startFan();
    } else if (command.equalsIgnoreCase("fan off")) {
      stopFan();
    } else if (command.equalsIgnoreCase("left")) {
      turnLeft();
    } else if (command.equalsIgnoreCase("right")) {
      turnRight();
    } else if (command.equalsIgnoreCase("center")) {
      centerFan();
    } else if (command.equalsIgnoreCase("low")) {
      setFanSpeed(50); // about 33% speed
    } else if (command.equalsIgnoreCase("medium")) {
      setFanSpeed(100); // about 66% speed
    } else if (command.equalsIgnoreCase("high")) {
      setFanSpeed(150); // 100% speed
    } else if (command.equalsIgnoreCase("full left")) {
      moveFullLeft();
    } else if (command.equalsIgnoreCase("full right")) {
      moveFullRight();
    } else if (command.equalsIgnoreCase("sweep")) {
      startSweep();
    } else if (command.equalsIgnoreCase("stop sweep")) {
      stopSweep();
    }
  }
    // Handle sweeping
  if (sweeping) {
    unsigned long currentTime = millis();
    if (currentTime - lastSweepTime >= sweepDelay) {
      lastSweepTime = currentTime;

      servoAngle += sweepDirection;
      if (servoAngle >= sweepMax) {
        servoAngle = sweepMax;
        sweepDirection = -1; // change direction
      }
      if (servoAngle <= sweepMin) {
        servoAngle = sweepMin;
        sweepDirection = 1; // change direction
      }
      fanServo.write(servoAngle);
    }
  }
}

void startFan(){
  motor1.drive(fanSpeed);
  Serial.println("Fan ON");
}

void stopFan() {
  motor1.brake(); // Brakes the motor
  Serial.println("Fan OFF");
}

void setFanSpeed(int speedValue) {
  fanSpeed = constrain(speedValue, -255, 255); // Can go reverse if needed
  motor1.drive(fanSpeed);
  Serial.print("Fan Speed Set To ");
  Serial.println(fanSpeed);
}

// Move fan slightly left
void turnLeft() {
  servoAngle = constrain(servoAngle + 30, 0, 180);
  fanServo.write(servoAngle);
  Serial.println("Turning Left");
}

// Move fan slightly right
void turnRight() {
  servoAngle = constrain(servoAngle - 30, 0, 180);
  fanServo.write(servoAngle);
  Serial.println("Turning Right");
}

// Center the fan
void centerFan() {
  servoAngle = 90;
  fanServo.write(servoAngle);
  Serial.println("Centering Fan");
}

// Move servo fully left
void moveFullLeft() {
  servoAngle = 0;
  fanServo.write(servoAngle);
  Serial.println("Moved to Full Left");
}

// Move servo fully right
void moveFullRight() {
  servoAngle = 180;
  fanServo.write(servoAngle);
  Serial.println("Moved to Full Right");
}

// Start sweeping
void startSweep() {
  sweeping = true;
  Serial.println("Started Sweeping...");
}

// Stop sweeping
void stopSweep() {
  sweeping = false;
  Serial.println("Stopped Sweeping...");
}