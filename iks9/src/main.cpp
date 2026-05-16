/*
 * BOGEN IKS9 Circumference Measurement Application
 * 
 * This application measures circumference and degrees with automatic reset
 * every 226.2mm (one complete magnetic disk revolution).
 * 
 * Features:
 * - Measures distance traveled (circumference)
 * - Calculates degrees of rotation
 * - Auto-resets every 226.2mm
 * - Manual reset via Z pulse
 * 
 * Pin Connections (ESP32):
 * IKS9 Signal -> ESP32 Pin
 * A (brown)  -> GPIO18
 * B (grey)   -> GPIO19
 * Z (pink)   -> GPIO21
 * V+ (red)   -> 5V
 * V- (blue)  -> GND
 */

#include <Arduino.h>
#include "IKS9Encoder.h"
#include "configure.h"

// Pin assignments for ESP32
IKS9Encoder encoder(PIN_A, PIN_B, PIN_Z, ENCODER_RESOLUTION_UM);

// Global variables
// Z pulse handling moved to IKS9Encoder class

void setup() {
    SERIAL_BEGIN(SERIAL_BAUD_RATE);
    SERIAL_PRINTLN("BOGEN IKS9 Circumference Measurement Application");
    SERIAL_PRINTLN("===============================================");
    SERIAL_PRINTLN("System Configuration:");
    SERIAL_PRINTLN("- Magnetic Disk: 72mm diameter, 460 poles");
    SERIAL_PRINTLN("- Circumference: 226.2mm per revolution");
    SERIAL_PRINTLN("- Auto-reset: Every 230mm (460 pulses)");
    SERIAL_PRINTLN("- Resolution: 5μm per pulse");
    SERIAL_PRINTLN("- Manual reset: GPIO21 Z pulse");
    
    // Configure Z pulse pin with internal pullup - handled by encoder class
    // pinMode(Z_PULSE_PIN, INPUT_PULLUP);
    // attachInterrupt(digitalPinToInterrupt(Z_PULSE_PIN), zPulseISR, RISING);
    
    // Initialize encoder
    if (encoder.begin()) {
        SERIAL_PRINTLN("IKS9 Encoder initialized successfully");
    } else {
        SERIAL_PRINTLN("IKS9 Encoder initialization failed!");
        while (1) {}
    }
    
    // Configure encoder
    encoder.setResolution(ENCODER_RESOLUTION_500);  // 5μm resolution per pulse
    encoder.setInvertDirection(false);              // Set true if direction is inverted
    encoder.enableZPulse(true);                     // Enable Z pulse for reset functionality
    
    SERIAL_PRINTLN("\nMeasurement started...");
    SERIAL_PRINTLN("Distance(mm)\tDegrees\t\tDirection\tPulses\t\tStatus");
    SERIAL_PRINTLN("============\t=======\t\t=========\t======\t\t======");
}

void loop() {
    // Check for Z pulse reset signal from encoder class
    if (encoder.getZPulseStatus()) {
        encoder.resetPosition();
        encoder.clearZPulse();
        SERIAL_PRINTLN("*** Z PULSE RESET ***");
        //delay(DEBOUNCE_DELAY_MS);  // Debounce delay
    }
    
    // Update speed calculation
    encoder.updateSpeed();
    
    // Get current measurements
    float distanceMM = encoder.getPositionMM();         // Distance in millimeters
    int32_t pulses = encoder.getPosition();             // Raw pulse count
    bool direction = encoder.getDirection();            // Direction
    
    // Calculate degrees (360° = 226.2mm circumference)
    int degrees = (distanceMM / MAGNETIC_DISK_CIRCUMFERENCE_MM) * DEGREES_PER_REVOLUTION;
    
    // Keep degrees in positive range for display (no normalization to 0-360 yet)
    // We want to see the full progression: 0° → 460 pulses (230mm)
    
    // Check for auto-reset at 460 pulses (230mm)
    if (pulses >= AUTO_RESET_PULSES || pulses <= -AUTO_RESET_PULSES) {
        encoder.resetPosition();
        SERIAL_PRINTLN("*** AUTO-RESET: 460 pulses (230mm) reached ***");
        return;  // Skip this loop iteration after reset
    }
    
    // Now normalize degrees for display (0-360 range)
    float displayDegrees = degrees;
    while (displayDegrees >= DEGREES_PER_REVOLUTION) displayDegrees -= DEGREES_PER_REVOLUTION;
    while (displayDegrees < 0.0) displayDegrees += DEGREES_PER_REVOLUTION;
    
    // Print data every 100ms
    static uint32_t lastPrint = 0;
    if (millis() - lastPrint >= PRINT_INTERVAL_MS) {
        SERIAL_PRINT(distanceMM, 2);
        SERIAL_PRINT("\t\t");
        SERIAL_PRINT(displayDegrees, 1);
        SERIAL_PRINT("°\t\t");
        SERIAL_PRINT(direction ? "FWD" : "REV");
        SERIAL_PRINT("\t\t");
        SERIAL_PRINT(pulses);
        SERIAL_PRINT("\t\t");
        
        // Status indicator
        if (pulses > (AUTO_RESET_PULSES * NEAR_RESET_THRESHOLD)) {  // Within 10% of reset (90% of 460 pulses)
            SERIAL_PRINTLN("NEAR RESET");
        } else {
            SERIAL_PRINTLN("OK");
        }
        
        lastPrint = millis();
    }
    
    // Check for errors
    if (encoder.hasError()) {
        SERIAL_PRINTLN("ERROR: IKS9 Encoder fault detected!");
        encoder.clearError();
    }
    
    delay(LOOP_DELAY_MS);  // Small delay for stable operation
}