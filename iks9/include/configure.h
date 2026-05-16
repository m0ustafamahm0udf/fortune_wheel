/*
 * BOGEN IKS9 Encoder Configuration Header
 * 
 * This file contains all configuration constants and settings
 * for the IKS9 encoder measurement application.
 */

#ifndef CONFIGURE_H
#define CONFIGURE_H

// Debug and Output Control
#define ENABLE_SERIAL_OUTPUT    1       // Set to 1 to enable serial output, 0 to disable

// Pin Definitions
#define PIN_A                   18      // Brown wire - Encoder A signal
#define PIN_B                   19      // Grey wire - Encoder B signal  
#define PIN_Z                   2      // Pink wire - Encoder Z signal
#define Z_PULSE_PIN             2      // Z pulse pin (same as PIN_Z)

// Encoder Configuration
#define ENCODER_RESOLUTION_UM   5.0     // 5μm resolution per pulse
#define ENCODER_RESOLUTION_500  500.0   // Alternative resolution setting

// Physical Constants
#define MAGNETIC_DISK_DIAMETER_MM       573.0    // Magnetic disk diameter
#define MAGNETIC_DISK_CIRCUMFERENCE_MM  1800   // 72mm diameter disk circumference
#define MAGNETIC_POLES                  3600     // Number of magnetic poles

// Auto-reset Configuration  
#define AUTO_RESET_DISTANCE_MM          1800   // Auto-reset distance
#define AUTO_RESET_PULSES               3600     // Auto-reset at 460 pulses

// Timing Constants
#define SERIAL_BAUD_RATE               115200   // Serial communication speed
#define PRINT_INTERVAL_MS              300      // Print data every 100ms
#define DEBOUNCE_DELAY_MS              100      // Z pulse debounce delay
#define LOOP_DELAY_MS                  1       // Main loop delay

// Status Thresholds
#define NEAR_RESET_THRESHOLD           0.9      // 90% of auto-reset pulses

// Mathematical Constants
#define DEGREES_PER_REVOLUTION         360    // Degrees in a full revolution

// Serial Output Macros (conditional compilation)
#if ENABLE_SERIAL_OUTPUT
    #define SERIAL_PRINT(...)       Serial.print(__VA_ARGS__)
    #define SERIAL_PRINTLN(...)     Serial.println(__VA_ARGS__)
    #define SERIAL_BEGIN(baud)      Serial.begin(baud)
#else
    #define SERIAL_PRINT(...)       ((void)0)
    #define SERIAL_PRINTLN(...)     ((void)0)
    #define SERIAL_BEGIN(baud)      ((void)0)
#endif

#endif // CONFIGURE_H
