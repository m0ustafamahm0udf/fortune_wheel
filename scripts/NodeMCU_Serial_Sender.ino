// ── Spin Configuration (Step & Delay) ──
float current_angle = 0.0;       // cumulative degrees
float step_degrees = 10.0;        // الدرجات المضافة في كل خطوة
unsigned long delay_ms = 1;    // التأخير بين كل خطوة بالمللي ثانية
bool is_running = false;

// ── Timing ──
unsigned long last_send_time_ms = 0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  delay(100);
  // إرسال القيم الأولية للرسم
  Serial.println("OK:STEP:" + String(step_degrees, 2));
  Serial.println("OK:DELAY:" + String(delay_ms));
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.indexOf("START") >= 0) {
      is_running = true;
      last_send_time_ms = millis();
      Serial.println("OK:START");

    } else if (command.indexOf("STOP") >= 0) {
      is_running = false;
      Serial.print("<");
      Serial.print(current_angle, 2);
      Serial.print(",0.0>");
      Serial.println();
      Serial.println("OK:STOP");

    } else if (command.indexOf("RESET") >= 0) {
      current_angle = 0.0;
      is_running = false;
      Serial.println("<0.00,0.0>");
      Serial.println("OK:RESET");

    } else if (command.indexOf("INFO") >= 0) {
      Serial.println("OK:STEP:" + String(step_degrees, 2));
      Serial.println("OK:DELAY:" + String(delay_ms));

    } else if (command.startsWith("STEP:")) {
      float s = command.substring(5).toFloat();
      if (s > 0.0) {
        step_degrees = s;
        Serial.println("OK:STEP:" + String(step_degrees, 2));
      }

    } else if (command.startsWith("DELAY:")) {
      unsigned long d = command.substring(6).toInt();
      if (d > 0) { 
        delay_ms = d;
        Serial.println("OK:DELAY:" + String(delay_ms));
      }
    }
  }

  unsigned long now = millis();

  // ── Step & Delay Loop ──
  if (is_running && (now - last_send_time_ms >= delay_ms)) {
    last_send_time_ms = now;

    // 1. زيادة الزاوية بالخطوة المحددة
    current_angle += step_degrees; // الدوران مستمر حتى يتم إرسال STOP

    // 2. إرسال البيانات للـ Serial للرسم في الشاشة
    Serial.print("<");
    Serial.print(current_angle, 2);
    Serial.println(",0.0>"); // نرسل السرعة 0.0 لأننا لغينا حسابات الفيزيا
  }
}
