float current_angle = 0.0;
const float STEP_ANGLE = 2.0;    // سرعة دوران العجلة للخطوة الواحدة
const int DELAY_MS = 50;         // التأخير بين كل قراءة (لضبط سرعة الإرسال)
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
      Serial.println(current_angle); // إرسال التحديث فوراً
      Serial.println("OK:RESET");
    }
  }

  // إذا كانت العجلة في حالة دوران، استمر في الحساب والإرسال
  if (is_running) {
    // 1. إرسال الزاوية الحالية عبر كابل الـ USB أولاً ليبدأ من 0
    Serial.println(current_angle);

    // 2. حساب الزاوية الجديدة للفة القادمة
    current_angle += STEP_ANGLE; 
    if (current_angle >= 360.0) {
      current_angle = 0.0; // إعادة التصفير بعد إكمال دورة كاملة
    }

    // 3. انتظار قليلاً قبل الإرسال القادم
    delay(DELAY_MS); 
  }
}
