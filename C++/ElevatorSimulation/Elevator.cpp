/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

#include "Floor.h" // from lab 9
#include "Rider.h"
#include "Elevator.h"

#include <iostream>
using std::cout;
using std::endl;

#include <vector>
using std::vector;

#include <cstdlib>
using std::abs;

int Elevator::elevatorID = 0; // initializing Elevator static member variable to zero
const int Elevator::IDLE = 0; // initializing Elevator static member variable to a unique numeric code
const int Elevator::UP = 1; // initializing Elevator static member variable to another unique numeric code
const int Elevator::DOWN = -1; // initializing Elevator static member variable to yet another unique numeric code

// initializing constructor for capacity, speed, and starting floor
Elevator::Elevator(const int capacity, const int speed, const Floor& startFloor)
: ID(elevatorID++), capacity(capacity), speed(speed), toFloor(0)
{
  location = startFloor.getLocation();
  direction = IDLE;
  doorOpen = true;
}

// non-inline functions
bool Elevator::isNearDestination() const // true if distance to destination is less than or equal to the speed
{
  int distance = 0;

  distance = abs(toFloor->getLocation() - location);  // calculate the distance from the elevator to the rider's destination floor
 
  return (distance <= speed);
}

void Elevator::moveToDestinationFloor() // set location to that of destination floor (if there is one)
{
  if(hasADestination())
    location = getDestination().getLocation();
}

vector<Rider> Elevator::removeRidersForDestinationFloor()
{
  vector<Rider> remove, remain;

  if (v.size() > 0) // if elevator has any riders
  {  
	for (int i = 0; i < v.size(); i++) // traverse vector of current riders
    {
      if (&(v[i].getDestination()) == toFloor) // if a rider's destination floor is same as elevator's destination floor
      {
	    remove.push_back(v[i]); // add rider to vector of removed riders
      } 
      else
      {
        remain.push_back(v[i]); // add rider to vector of remaining riders
      }
    }

    v = remain; // reassign elevator rider vector to vector of remaining riders
  }

  return remove; // return vector of removed riders
}

void Elevator::addRiders(const vector<Rider>& riders)
{
  if (riders.empty() == true) // if the parameter vector is empty
  {
    return; // exit the function
  }

  for (unsigned int i = 0; i < riders.size(); i++) // traverse the parameter vector
  {
    if (getAvailableSpace() > 0 ) // if there is still room on the elevator 
      v.push_back(riders[i]); // add the rider to the elevator's rider vector
  }
}

void Elevator::setDestinationBasedOnRiders()
{
  if (getRiderCount() == 0) // if there are no riders on the elevator
  {
    return; // exit the function
  }

  // create an int to track the closest rider's distance to his destination
  // initialize it to a negative number (to signify that it is not yet set)
  int ridersDistToDest = -1; 

  for (int i = 0; i < v.size(); i++) // traverse the vector of elevator riders
  {
      int distance = abs(location - v[i].getDestination().getLocation());  // calculate the distance from the elevator to the rider's destination floor

      if (ridersDistToDest < 0 || ridersDistToDest > distance) // if closest rider's distance is negative OR is greater than the above value
      {
         ridersDistToDest = distance; // set closest rider's distance to the above value
         setDestination(&(v[i].getDestination())); // set elevator's destination floor to rider's destination floor
    }
  }

}

// friend function
ostream& operator<<(ostream& out, const Elevator& e)
{
  // print location and status
  out << "Location: " << e.getLocation() << ", Direction:";

  if (e.isIdle())
  {
    out << " idle, ";
  }
  else if (e.isDirectionUp())
  {
    out << " going up, ";
  }
  else if (e.isDirectionDown())
  {
    out << " going down, ";
  }

  if (e.isDoorOpen())
    out << "Door status: open";
  else
    out << "Door status: closed";

  if (e.getRiderCount() == 0)
    out << ", Riders: no riders." << endl;
  else 
    out << ", Riders: " << e.getRiderCount() << endl;

  return out;
}
