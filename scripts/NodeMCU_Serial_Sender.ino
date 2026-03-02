float current_angle = 0.0;
const float STEP_ANGLE = 1.0;
float delay_ms = 0.1;
bool is_running = false;
unsigned long last_send_time_us = 0;  // microseconds

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
      last_send_time_us = micros();
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
      float new_delay = command.substring(6).toFloat();
      if (new_delay >= 0.1 && new_delay <= 5000.0) {
        delay_ms = new_delay;
        Serial.println("OK:SPEED:" + String(delay_ms, 1));
      }
    }
  }

  // non-blocking: ارسل الزاوية فقط لما يعدي الوقت المحدد (بالـ microseconds)
  unsigned long delay_us = (unsigned long)(delay_ms * 1000.0);
  if (is_running && (micros() - last_send_time_us >= delay_us)) {
    last_send_time_us = micros();

    Serial.print("<"); Serial.print(current_angle); Serial.print(","); Serial.print(delay_ms, 1); Serial.println(">");

    current_angle += STEP_ANGLE;
    if (current_angle >= 360.0) {
      current_angle = 0.0;
    }
  }
}
