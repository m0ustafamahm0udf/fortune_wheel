/*
 * BOGEN IKS9 Incremental Magnetic Sensing Head Driver - Header File
 * 
 * Features:
 * - Quadrature encoder decoding with interrupt-based counting
 * - Direction detection and position tracking  
 * - Reference pulse (Z) handling for absolute positioning
 * - Speed/velocity calculation
 * - Error detection and status monitoring
 * 
 * Hardware Requirements:
 * - BOGEN IKS9 sensor configured for Push-Pull TTL output (0-5V)
 * - 5V power supply for sensor
 * - Appropriate magnetic scale/tape
 * 
 * Pin Connections (ESP32):
 * IKS9 Signal -> ESP32 Pin
 * A (brown)  -> GPIO18
 * B (grey)   -> GPIO19
 * Z (pink)   -> GPIO21
 * V+ (red)   -> 5V
 * V- (blue)  -> GND
 */

#ifndef IKS9_ENCODER_H
#define IKS9_ENCODER_H

#include <Arduino.h>

class IKS9Encoder {
private:
    // Pin assignments
    uint8_t pinA, pinB, pinZ;
    
    // Position and state variables
    volatile long position;
    volatile bool direction;
    volatile bool zPulseDetected;
    volatile bool errorState;
    
    // Resolution and configuration
    float resolution_um;           // Resolution in micrometers
    bool invertDirection;
    bool zPulseEnabled;
    
    // Speed calculation
    long lastPosition;
    unsigned long lastTime;
    float currentSpeed;
    
    // Quadrature state tracking
    volatile uint8_t lastState;
    
    // ISR pointers for interrupt handling
    static IKS9Encoder* instance;
    static void IRAM_ATTR handleInterruptA();
    static void IRAM_ATTR handleInterruptB();
    static void IRAM_ATTR handleInterruptZ();

public:
    IKS9Encoder(uint8_t pinA, uint8_t pinB, uint8_t pinZ, float resolution_um = 1.0);
    
    // Initialization
    bool begin();
    
    // Configuration
    void setResolution(float resolution_um);
    void setInvertDirection(bool invert);
    void enableZPulse(bool enable);
    
    // Position functions
    long getPosition();
    float getPositionMM();
    float getPositionUM();
    void resetPosition();
    
    // Direction and speed
    bool getDirection();
    float getSpeed();
    void updateSpeed();
    
    // Z pulse functions
    bool getZPulseStatus();
    void clearZPulse();
    
    // Error handling
    bool hasError();
    void clearError();
    
    // Internal functions
    void handleEncoderISR();
    void handleZPulseISR();
    void updatePosition();
    void detectError();
};

#endif // IKS9_ENCODER_H
