#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX

void setup() {
  Serial.begin(9600); // Communication with PC
  mySerial.begin(9600); // Communication with Python script
  Serial.println("Arduino is ready.");
}

void loop() {
  if (mySerial.available()) {
    String message = mySerial.readStringUntil('\n');
    Serial.print("Received: ");
    Serial.println(message);

    // Process the message (e.g., echo it back for now)
    String response = "Arduino received: " + message;
    mySerial.println(response);
  }

  delay(100); // Small delay to avoid overwhelming the serial buffer
}
