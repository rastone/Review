/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/
//
// Floor class definition
#include <vector>
using std::vector;

#include <iostream>
using std::ostream;

#include <string>
using std::string;

#include "Rider.h"

#ifndef FLOOR_H
#define FLOOR_H

class Floor // all functions are inline
{
  private:
    const string NAME; // name of floor, for example: Mezzanine
    const int locationOfFloor; // as measured in int inches above ground level
    vector<Rider> upRiders; // affected by addNewRider, removeUpRiders,...
    vector<Rider> downRiders; // ...and removeDownRiders functions

  public:
    Floor(const int l, const char* const n) : locationOfFloor(l), NAME(n) {} // name and location (inches above ground) of floor

    // inline functions
    int getLocation() const { return locationOfFloor; } // returns the floor's location
    bool hasRidersWaiting() const { return (hasUpRiders() || hasDownRiders()); }
    bool hasUpRiders() const { return !(upRiders.empty()); }
    bool hasDownRiders() const { return !(downRiders.empty()); }
    int getUpRiderCount() const { return upRiders.size(); } 
    int getDownRiderCount() const { return downRiders.size(); }
    string getName() const { return NAME; }

    // non-inline functions
    bool isPreferredDirectionUp() const; // based on Rider with smallest ID
    void addNewRider(const Rider&); // add to up- or down-vector
    vector<Rider> removeUpRiders(int); // int is max #of riders...
    vector<Rider> removeDownRiders(int); //...to move onto elevator

    // just in case you prefer to use "if (...== *toFloor)" 
    //  in Elevator::removeRidersForDestinationFloor(), instead of "...== toFloor)"
    bool operator==(const Floor& floor) const {return NAME == floor.NAME;}

    friend ostream& operator<<(ostream&, const Floor&); // say name, location, #'s of up/down riders waiting
};

#endif