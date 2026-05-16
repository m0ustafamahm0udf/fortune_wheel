# IKS9 Quick Start 

## 1. التوصيل السريع

```text
IKS9          →     ESP32
─────────────────────────────
A  (Brown)    →     GPIO 18
B  (Grey)     →     GPIO 19
Z  (Pink)     →     GPIO 2
V+ (Red)      →     5V / VIN
V− (Blue)     →     GND
```

## 2. حرق الـ firmware على الـ ESP32

من داخل مجلد `iks9/`:

```bash
cd iks9
pio run
pio run --target upload
pio device monitor
```

لو ظهر سطر قريب من ده، يبقى الجهاز شغال:

```text
IKS9 Encoder initialized successfully
0.00    0.0°    FWD    0    OK
```

## 3. معرفة اسم الـ Serial Port

اقفل الـ monitor الأول، ثم:

على macOS:

```bash
ls /dev/cu.*
```

على Linux / Raspberry Pi:

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

## 4. ضبط البورت في الـ Python

افتح [`fortune_wheel/config.py`](./fortune_wheel/config.py) وعدّل:

```python
SERIAL_PORT = '/dev/cu.usbserial-0001'
```

وحط مكانه اسم البورت الفعلي عندك.

## 5. تثبيت المتطلبات

```bash
python3 -m pip install pygame pyserial
```

لو التثبيت المباشر اشتغل، كمل على التشغيل.

## 6. لو محتاج `venv` للمكتبات

استخدم الخطوات دي لو:

- `pip install` فشل
- ظهر `ModuleNotFoundError`
- عايز تعزل مكتبات المشروع عن النظام

من داخل `scripts/`:

```bash
cd scripts
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pygame pyserial
```

بعدها شغّل البرنامج من نفس الـ `venv`:

```bash
python fortune_wheel_gui.py
```

ولو حبيت تخرج من الـ `venv` بعد ما تخلص:

```bash
deactivate
```

## 7. تشغيل الواجهة

من داخل `scripts/`:

```bash
cd scripts
python3 fortune_wheel_gui.py
```

أو:

```bash
python3 -m fortune_wheel
```

ولو أنت مفعّل `venv` بالفعل، استخدم:

```bash
python fortune_wheel_gui.py
```

## 8. الاستخدام أثناء التشغيل

- لف القرص الحقيقي: العجلة على الشاشة تتحرك بنفس الزاوية.
- `S`: يبدأ جولة جديدة.
- `X`: يثبت النتيجة ويظهر الفائز.
- `R`: يعيد الصفر للزاوية الحالية.
- `Q` أو `Esc`: خروج.

## 9. التأكد السريع

- لو الحالة ظهرت `Connected` باللون الأخضر، فالاتصال شغال.
- لو لفيت القرص والزاوية اتغيرت، فالقراءة سليمة.
- لو ضغطت `X` وظهر `Winner: No ...`، فالنظام شغال بالكامل.

## 10. لو في مشكلة

- `Disconnected`: غالبًا اسم البورت غلط في `config.py`.
- مفيش حركة في الزاوية: راجع A و B و GND.
- الاتجاه معكوس: بدّل A مع B.
