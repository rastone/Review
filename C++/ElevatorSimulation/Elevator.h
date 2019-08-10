/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

// Elevator class definition
#ifndef ELEVATOR_H
#define ELEVATOR_H

#include "Rider.h"

#include <iostream>
using std::ostream;

#include <vector>
using std::vector;

class Floor; // forward declaration

class Elevator
{
  // class-defined constants
  static int elevatorID; // initialize to zero; use to assign unique ID to each elevator
  static const int IDLE; // a unique numeric code
  static const int UP; // another unique numeric code
  static const int DOWN; // yet another unique numeric code

  // private member variables
  const int ID; // a unique identifier
  const int capacity; // max number of riders, set in constructor
  const int speed; // inches per second, up or down, set in constructor
  const Floor* toFloor; // destination floor, initialized in constructor to zero
  int location; // inches above ground level, initialized in constructor based on starting floor
  int direction; // equal to IDLE, UP, DOWN, initialized to IDLE in constructor
  bool doorOpen; // initialized to true in constructor
  vector<Rider> v;

  public:
    Elevator(const int, const int, const Floor&); // capacity, speed, and starting floor
    
    // inline functions
    bool isDoorOpen() const { return doorOpen; } // returns value of doorOpen
    bool isIdle() const { return (direction == IDLE); } // returns true if direction is IDLE
    bool isDirectionUp() const { return (direction == UP); } // returns true if direction is UP
    bool isDirectionDown() const { return (direction == DOWN); } // returns true if direction is DOWN
    void closeDoor() { doorOpen = false; } // set doorOpen to false
    void openDoor() { doorOpen = true; } // set doorOpen to true
    void setIdle() { direction = IDLE; } // set direction to IDLE
    void setDirectionUp() { direction = UP; } // set direction to UP
    void setDirectionDown() { direction = DOWN; } // set direction to DOWN
    void moveUp() { location += speed; } // increment location by #inches per second speed of the elevator
    void moveDown() { location -= speed; } // decrement location by #inches per second speed of the elevator
    void setDestination(const Floor* floor) { toFloor = floor; } // set toFloor pointer
    bool hasADestination() const { return (toFloor != 0); } // return false if toFloor is zero
    const Floor& getDestination() const { return *toFloor; } // return reference to toFloor (warning!)
    int getLocation() const { return location; } // return location value

    bool hasRiders() const { return v.empty(); } // returns false if riders vector is empty
    int getRiderCount() const { return v.size(); } // return size of riders vector
    int getCapacity() const { return capacity; } // return capacity
    int getAvailableSpace() const { return (capacity - v.size()); } // return capacity minus size of riders vector

    // non-inline functions
    bool isNearDestination() const; // true if distance to destination is less than or equal to the speed
    void moveToDestinationFloor(); // set location to that of destination floor (if there is one)

    vector<Rider> removeRidersForDestinationFloor(); // remove riders from vector whose destination is 
    void addRiders(const vector<Rider>&); // copy riders from parameter vector to riders vector
    void setDestinationBasedOnRiders(); // reset toFloor based on riders' destinations
    
    // friend function
    friend ostream& operator<<(ostream&, const Elevator&);
};

#endif