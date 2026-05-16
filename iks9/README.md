# BOGEN IKS9 Encoder Interface

A robust Arduino/ESP32 library and application for interfacing with BOGEN IKS9 incremental magnetic sensing heads. This project provides precise position measurement, direction detection, and automatic reset functionality for industrial automation and measurement applications.

## 📋 Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## ✨ Features

- **Quadrature Encoding**: Full A/B phase decoding with direction detection
- **Z-Pulse Reset**: Automatic position reset using reference pulse
- **Configurable Resolution**: Support for different encoder resolutions (default: 5μm)
- **Auto-Reset**: Programmable automatic reset at specified pulse counts
- **Error Detection**: Built-in sensor fault detection and monitoring
- **Speed Calculation**: Real-time velocity measurement
- **Serial Control**: Configurable debug output (can be disabled for production)
- **Interrupt-Based**: Efficient interrupt-driven position tracking
- **Industrial Grade**: Designed for robust industrial applications

## 🔧 Hardware Requirements

### Microcontroller
- **ESP32** (recommended)
- Arduino compatible boards with interrupt-capable pins

### Sensor
- **BOGEN IKS9** incremental magnetic sensing head
- Configured for Push-Pull TTL output (0-5V)
- Magnetic scale/tape compatible with IKS9

### Power Supply
- **5V** for IKS9 sensor
- **3.3V** for ESP32

## 📦 Installation

### Prerequisites
- [PlatformIO](https://platformio.org/) or Arduino IDE
- ESP32 development board

### Using PlatformIO (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd IKS_encoder
   ```

2. **Open in PlatformIO:**
   ```bash
   pio run
   ```

3. **Upload to device:**
   ```bash
   pio run --target upload
   ```

### Using Arduino IDE

1. Copy the `src/` and `include/` folders to your Arduino sketch directory
2. Install ESP32 board support if not already installed
3. Select your ESP32 board and upload

## 🚀 Quick Start

### 1. Hardware Connections

Connect your IKS9 sensor to the ESP32:

| IKS9 Signal | Color  | ESP32 Pin | Description |
|-------------|--------|-----------|-------------|
| A           | Brown  | GPIO18    | Phase A signal |
| B           | Grey   | GPIO19    | Phase B signal |
| Z           | Pink   | GPIO21    | Index/reference pulse |
| V+          | Red    | 5V        | Power supply |
| V-          | Blue   | GND       | Ground |

### 2. Basic Usage

```cpp
#include <Arduino.h>
#include "IKS9Encoder.h"
#include "configure.h"

// Create encoder instance
IKS9Encoder encoder(PIN_A, PIN_B, PIN_Z, ENCODER_RESOLUTION_UM);

void setup() {
    Serial.begin(115200);
    
    // Initialize encoder
    encoder.begin();
    encoder.setResolution(5.0);  // 5μm per pulse
    encoder.enableZPulse(true);  // Enable Z pulse reset
}

void loop() {
    // Read position
    float position_mm = encoder.getPositionMM();
    int32_t pulses = encoder.getPosition();
    bool direction = encoder.getDirection();
    
    // Print results
    Serial.print("Position: ");
    Serial.print(position_mm, 2);
    Serial.print(" mm, Pulses: ");
    Serial.print(pulses);
    Serial.print(", Direction: ");
    Serial.println(direction ? "FWD" : "REV");
    
    delay(100);
}
```

## ⚙️ Configuration

All configuration is centralized in `include/configure.h`. Modify this file to customize the behavior:

### Key Configuration Options

```cpp
// Enable/Disable Serial Output
#define ENABLE_SERIAL_OUTPUT    1       // 1 = Enable, 0 = Disable

// Pin Assignments
#define PIN_A                   18      // Encoder A signal
#define PIN_B                   19      // Encoder B signal  
#define PIN_Z                   21      // Encoder Z signal

// Encoder Settings
#define ENCODER_RESOLUTION_UM   5.0     // Resolution in micrometers
#define MAGNETIC_DISK_CIRCUMFERENCE_MM  226.2   // Physical circumference

// Auto-Reset Settings
#define AUTO_RESET_PULSES       460     // Auto-reset at this pulse count

// Timing Parameters
#define PRINT_INTERVAL_MS       100     // Data output interval
#define DEBOUNCE_DELAY_MS       100     // Z pulse debounce time
```

### Serial Output Control

To disable serial output for production use:
```cpp
#define ENABLE_SERIAL_OUTPUT    0
```

This completely removes all serial code during compilation, improving performance and reducing memory usage.

## 📚 API Reference

### IKS9Encoder Class

#### Constructor
```cpp
IKS9Encoder(uint8_t pinA, uint8_t pinB, uint8_t pinZ, float resolution_um = 1.0)
```
- `pinA`: GPIO pin for encoder A signal
- `pinB`: GPIO pin for encoder B signal  
- `pinZ`: GPIO pin for encoder Z signal
- `resolution_um`: Resolution in micrometers per pulse

#### Initialization Methods

```cpp
bool begin()
```
Initialize the encoder. Returns `true` if successful.

```cpp
void setResolution(float resolution_um)
```
Set the encoder resolution in micrometers per pulse.

```cpp
void setInvertDirection(bool invert)
```
Invert the direction reading if needed.

```cpp
void enableZPulse(bool enable)
```
Enable or disable Z pulse functionality.

#### Position Methods

```cpp
long getPosition()
```
Get the current position in pulses.

```cpp
float getPositionMM()
```
Get the current position in millimeters.

```cpp
float getPositionUM()
```
Get the current position in micrometers.

```cpp
void resetPosition()
```
Reset the position counter to zero.

#### Status Methods

```cpp
bool getDirection()
```
Get the current direction. Returns `true` for forward, `false` for reverse.

```cpp
float getSpeed()
```
Get the current speed in mm/s.

```cpp
void updateSpeed()
```
Update the speed calculation (call regularly in main loop).

#### Z Pulse Methods

```cpp
bool getZPulseStatus()
```
Check if a Z pulse has been detected.

```cpp
void clearZPulse()
```
Clear the Z pulse detection flag.

#### Error Handling

```cpp
bool hasError()
```
Check if an error has been detected.

```cpp
void clearError()
```
Clear the error flag.

```cpp
void detectError()
```
Perform error detection (call regularly in main loop).

## 💡 Usage Examples

### Example 1: Basic Position Reading

```cpp
void loop() {
    encoder.updateSpeed();
    
    float position = encoder.getPositionMM();
    bool direction = encoder.getDirection();
    
    Serial.print("Position: ");
    Serial.print(position, 2);
    Serial.print(" mm, Direction: ");
    Serial.println(direction ? "Forward" : "Reverse");
    
    delay(100);
}
```

### Example 2: Auto-Reset with Z Pulse

```cpp
volatile bool zPulseDetected = false;

void IRAM_ATTR zPulseISR() {
    zPulseDetected = true;
}

void setup() {
    // ... other setup code ...
    
    pinMode(PIN_Z, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_Z), zPulseISR, RISING);
    encoder.enableZPulse(true);
}

void loop() {
    if (zPulseDetected) {
        encoder.resetPosition();
        zPulseDetected = false;
        Serial.println("Position reset by Z pulse");
    }
    
    // ... rest of loop ...
}
```

### Example 3: Speed Measurement

```cpp
void loop() {
    encoder.updateSpeed();
    
    float speed = encoder.getSpeed();
    float position = encoder.getPositionMM();
    
    Serial.print("Speed: ");
    Serial.print(speed, 2);
    Serial.print(" mm/s, Position: ");
    Serial.print(position, 2);
    Serial.println(" mm");
    
    delay(50);  // Update at 20Hz
}
```

### Example 4: Error Monitoring

```cpp
void loop() {
    encoder.detectError();
    
    if (encoder.hasError()) {
        Serial.println("⚠️  Encoder Error Detected!");
        encoder.clearError();
        
        // Take corrective action
        // - Check connections
        // - Verify power supply
        // - Reset if necessary
    }
    
    // ... normal operation ...
}
```

## 🔧 Build and Run

### PlatformIO Commands

```bash
# Build project
pio run

# Upload to device
pio run --target upload

# Monitor serial output
pio device monitor

# Build and upload then monitor
pio run --target upload && pio device monitor

# Clean build
pio run --target clean
```

### Monitor Output

When running with serial output enabled, you'll see:

```
BOGEN IKS9 Circumference Measurement Application
===============================================
System Configuration:
- Magnetic Disk: 72mm diameter, 460 poles
- Circumference: 226.2mm per revolution
- Auto-reset: Every 230mm (460 pulses)
- Resolution: 5μm per pulse
- Manual reset: GPIO21 Z pulse

IKS9 Encoder initialized successfully

Measurement started...
Distance(mm)    Degrees         Direction       Pulses          Status
============    =======         =========       ======          ======
0.00            0.0°            FWD             0               OK
0.50            0.8°            FWD             100             OK
1.00            1.6°            FWD             200             OK
```

## 🐛 Troubleshooting

### Common Issues

**1. Encoder not initializing**
- Check wiring connections
- Verify 5V power supply to IKS9
- Ensure correct pin assignments in `configure.h`

**2. Incorrect direction**
- Use `encoder.setInvertDirection(true)` to reverse direction
- Check A and B signal wiring

**3. Missing pulses**
- Verify signal quality with oscilloscope
- Check for electrical noise
- Ensure proper grounding

**4. Z pulse not working**
- Confirm Z signal connection to GPIO21
- Check interrupt configuration
- Verify Z pulse is enabled: `encoder.enableZPulse(true)`

**5. Serial output not working**
- Ensure `ENABLE_SERIAL_OUTPUT` is set to `1`
- Check baud rate (default: 115200)
- Verify USB connection

### Debug Tips

1. **Enable verbose output** by setting debug flags in `configure.h`
2. **Check signal integrity** with an oscilloscope
3. **Verify timing** - ensure adequate loop timing for high-speed applications
4. **Monitor error flags** using `encoder.hasError()`







