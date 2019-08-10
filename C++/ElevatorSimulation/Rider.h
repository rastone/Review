/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/
//
// Rider class definition
#ifndef RIDER_H
#define RIDER_H

class Floor; // forward declaration

class Rider
{
  private:
    const int riderID; // to uniquely identify a rider
    const Floor* const destFloor; // representing a rider's destination floor
    static int trackAssignID;
  public:
    Rider(const Floor &floor) : riderID(trackAssignID++), destFloor(&floor) {}
    const Floor& getDestination() const { return *destFloor; }
    bool operator<(const Rider &r) const { return riderID < r.riderID; }
    bool operator==(const Rider r) const { return riderID == r.riderID; }
    const Rider& operator=(const Rider r) { const_cast<int&>(riderID) = r.riderID; const_cast<const Floor*&>(destFloor) = r.destFloor; return *this; }
};

#endif