/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/
//
// Building class definition
#ifndef BUILDING_H
#define BUILDING_H

#include <iostream>
using std::ostream;

#include <vector>
using std::vector;

class Floor; // forward declaration
class Elevator; // forward declaration

class Building
{
  private:
    vector<Floor*> floors;
    vector<Elevator*> elevators;
    int simTime;

  public:
    Building(); // default constructor
    ~Building(); // destructor
    friend ostream& operator<<(ostream&, const Building&);

    Building& step(int); // the n of randomly-placed riders to add
    void getDifferentInts(int, int&, int&); // max, n1, n2

    // inline functions
    // return #of floors in the vector of Floor*'s
    int getFloorCount() const { return floors.size(); }

    // return #of elevators in the vector of Elevator*'s
    int getElevatorCount() const { return elevators.size(); }

    // return a reference to the "indexth" floor
    const Floor& getFloor(int index) const { return *(floors[index]); }

    // return a reference to the "indexth" elevator
    const Elevator& getElevator(int index) const { return *(elevators[index]); }
};

#endif

