/*
 * BOGEN IKS9 Incremental Magnetic Sensing Head Driver - Implementation File
 * 
 * This file contains the implementation of the IKS9Encoder class for
 * interfacing with BOGEN IKS9 magnetic encoder sensors.
 */

#include "IKS9Encoder.h"

// Static instance pointer
IKS9Encoder* IKS9Encoder::instance = nullptr;

// Constructor
IKS9Encoder::IKS9Encoder(uint8_t pinA, uint8_t pinB, uint8_t pinZ, float resolution_um) {
    this->pinA = pinA;
    this->pinB = pinB;
    this->pinZ = pinZ;
    this->resolution_um = resolution_um;
    
    position = 0;
    direction = true;
    zPulseDetected = false;
    errorState = false;
    invertDirection = false;
    zPulseEnabled = true;
    lastState = 0;
    lastPosition = 0;
    lastTime = 0;
    currentSpeed = 0.0;
    
    instance = this;
}

// Initialize the encoder
bool IKS9Encoder::begin() {
    // Configure pins
    pinMode(pinA, INPUT_PULLUP);
    pinMode(pinB, INPUT_PULLUP);
    if (zPulseEnabled) {
        pinMode(pinZ, INPUT_PULLUP);
    }
    
    // Read initial state
    lastState = (digitalRead(pinA) << 1) | digitalRead(pinB);
    
    // Attach interrupts
    attachInterrupt(digitalPinToInterrupt(pinA), handleInterruptA, CHANGE);
    attachInterrupt(digitalPinToInterrupt(pinB), handleInterruptB, CHANGE);
    if (zPulseEnabled) {
        attachInterrupt(digitalPinToInterrupt(pinZ), handleInterruptZ, CHANGE);
    }
    
    lastTime = micros();
    return true;
}

// Static interrupt handlers
void IRAM_ATTR IKS9Encoder::handleInterruptA() {
    if (instance) instance->handleEncoderISR();
}

void IRAM_ATTR IKS9Encoder::handleInterruptB() {
    if (instance) instance->handleEncoderISR();
}

void IRAM_ATTR IKS9Encoder::handleInterruptZ() {
    if (instance) instance->handleZPulseISR();
}

// Configuration functions
void IKS9Encoder::setResolution(float resolution_um) {
    this->resolution_um = resolution_um;
}

void IKS9Encoder::setInvertDirection(bool invert) {
    this->invertDirection = invert;
}

void IKS9Encoder::enableZPulse(bool enable) {
    this->zPulseEnabled = enable;
}

// Position functions
long IKS9Encoder::getPosition() {
    return position;
}

float IKS9Encoder::getPositionMM() {
    return (position * resolution_um) / 1000.0;
}

float IKS9Encoder::getPositionUM() {
    return position * resolution_um;
}

void IKS9Encoder::resetPosition() {
    position = 0;
    lastPosition = 0;
}

// Direction and speed
bool IKS9Encoder::getDirection() {
    return invertDirection ? !direction : direction;
}

float IKS9Encoder::getSpeed() {
    return currentSpeed;
}

void IKS9Encoder::updateSpeed() {
    unsigned long currentTime = micros();
    long currentPos = getPosition();
    
    if (currentTime - lastTime >= 50000) { // Update every 50ms
        long deltaPosition = currentPos - lastPosition;
        unsigned long deltaTime = currentTime - lastTime;
        
        // Speed in mm/s (convert from μm/μs to mm/s)
        currentSpeed = (deltaPosition * resolution_um * 1000.0) / deltaTime;
        
        lastPosition = currentPos;
        lastTime = currentTime;
    }
}

// Z pulse functions
bool IKS9Encoder::getZPulseStatus() {
    return zPulseDetected;
}

void IKS9Encoder::clearZPulse() {
    zPulseDetected = false;
}

// Error handling
bool IKS9Encoder::hasError() {
    return errorState;
}

void IKS9Encoder::clearError() {
    errorState = false;
}

// Z pulse ISR
void IKS9Encoder::handleZPulseISR() {
    zPulseDetected = true;
}

// Quadrature decoder ISR
void IKS9Encoder::handleEncoderISR() {
    updatePosition();
}

// Update position based on quadrature signals
void IKS9Encoder::updatePosition() {
    uint8_t currentState = (digitalRead(pinA) << 1) | digitalRead(pinB);
    
    // Quadrature decode table
    int8_t stateChange = 0;
    uint8_t transition = (lastState << 2) | currentState;
    
    switch (transition) {
        case 0b0001: case 0b0111: case 0b1110: case 0b1000:
            stateChange = 1;
            direction = true;
            break;
        case 0b0010: case 0b1011: case 0b1101: case 0b0100:
            stateChange = -1;
            direction = false;
            break;
        default:
            stateChange = 0; // Invalid transition or no change
            break;
    }
    
    position += stateChange;
    lastState = currentState;
}

// Enhanced error detection
void IKS9Encoder::detectError() {
    static unsigned long lastErrorCheck = 0;
    unsigned long currentTime = micros();
    
    if (currentTime - lastErrorCheck > 100000) { // Check every 100ms
        // Check for stuck signals or impossible states
        int pinA_state = digitalRead(pinA);
        int pinB_state = digitalRead(pinB);
        
        static uint8_t lastInvalidState = 0xFF;
        static unsigned long invalidStateStart = 0;
        
        uint8_t currentState = (pinA_state << 1) | pinB_state;
        if (currentState == lastInvalidState) {
            if (currentTime - invalidStateStart > 1000000) { // 1 second of same state
                errorState = true;
            }
        } else {
            invalidStateStart = currentTime;
            lastInvalidState = currentState;
        }
        
        lastErrorCheck = currentTime;
    }
}
