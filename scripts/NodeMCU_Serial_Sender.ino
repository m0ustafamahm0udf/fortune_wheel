float current_angle = 0.0;
const float STEP_ANGLE = 1.0;    // سرعة دوران العجلة للخطوة الواحدة
int delay_ms = 50;               // التأخير بين كل قراءة (لضبط سرعة الإرسال) - يمكن تغييره عبر أمر SPEED
bool is_running = false;         // حالة الدوران (متوقفة أم تعمل)

void setup() {
  // تهيئة الاتصال التسلسلي (Serial) مع جهاز الكمبيوتر/الراسبيري بسرعة 115200
  Serial.begin(115200);
  // إضافة مهلة زمنية قصيرة لمنع توقف الكود (Blocking) أثناء القراءة
  Serial.setTimeout(10); 
}

void loop() {
  // استقبال الأوامر من السيريال (عبر كابل الـ USB)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // إزالة أي مسافات أو أسطر إضافية

    if (command.indexOf("START") >= 0) {
      current_angle = 0.0; // التصفير لضمان أن يبدأ دائماً من 0
      is_running = true;
      Serial.println("OK:START");
    } else if (command.indexOf("STOP") >= 0) {
      is_running = false;
      Serial.println("OK:STOP");
    } else if (command.indexOf("RESET") >= 0) {
      current_angle = 0.0;
      Serial.print("<"); Serial.print(current_angle); Serial.println(">");
      Serial.println("OK:RESET");
    } else if (command.startsWith("SPEED:")) {
      int new_delay = command.substring(6).toInt();
      if (new_delay >= 1 && new_delay <= 5000) {
        delay_ms = new_delay;
        Serial.println("OK:SPEED:" + String(delay_ms));
      }
    }
  }

  // إذا كانت العجلة في حالة دوران، استمر في الحساب والإرسال
  if (is_running) {
    // 1. إرسال الزاوية الحالية عبر كابل الـ USB أولاً ليبدأ من 0
    Serial.print("<"); Serial.print(current_angle); Serial.println(">");

    // 2. حساب الزاوية الجديدة للفة القادمة
    current_angle += STEP_ANGLE; 
    if (current_angle >= 360.0) {
      current_angle = 0.0; // إعادة التصفير بعد إكمال دورة كاملة
    }

    // 3. انتظار قليلاً قبل الإرسال القادم
    delay(delay_ms); 
  }
}
