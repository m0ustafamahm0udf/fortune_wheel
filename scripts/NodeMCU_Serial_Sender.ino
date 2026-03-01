float current_angle = 0.0;
const float STEP_ANGLE = 1.0;
int delay_ms = 5;
bool is_running = false;
unsigned long last_send_time = 0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
}

void loop() {
  // استقبال الأوامر من السيريال
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.indexOf("START") >= 0) {
      current_angle = 0.0;
      is_running = true;
      last_send_time = millis();
      Serial.println("OK:START");
    } else if (command.indexOf("STOP") >= 0) {
      is_running = false;
      Serial.println("OK:STOP");
    } else if (command.indexOf("RESET") >= 0) {
      current_angle = 0.0;
      is_running = false;
      Serial.print("<"); Serial.print(current_angle); Serial.print(","); Serial.print(delay_ms); Serial.println(">");
      Serial.println("OK:RESET");
    } else if (command.startsWith("SPEED:")) {
      int new_delay = command.substring(6).toInt();
      if (new_delay >= 1 && new_delay <= 5000) {
        delay_ms = new_delay;
        Serial.println("OK:SPEED:" + String(delay_ms));
      }
    }
  }

  // non-blocking: ارسل الزاوية فقط لما يعدي الوقت المحدد
  if (is_running && (millis() - last_send_time >= (unsigned long)delay_ms)) {
    last_send_time = millis();

    Serial.print("<"); Serial.print(current_angle); Serial.print(","); Serial.print(delay_ms); Serial.println(">");

    current_angle += STEP_ANGLE;
    if (current_angle >= 360.0) {
      current_angle = 0.0;
    }
  }
}
