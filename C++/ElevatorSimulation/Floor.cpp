/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

#include <iostream>
using std::cout;
using std::endl;

#include <vector>
using std::vector;

#include "Floor.h"
#include "Rider.h"

// non-inline functions
void Floor::addNewRider(const Rider& rider) // add to up- or down-vector
{
  // if added rider's destination is greater than the floor's location
  if (rider.getDestination().getLocation() > this->getLocation())
  {
     // add rider to the upRiders vector
     upRiders.push_back(rider);
  }
  else // else
    downRiders.push_back(rider); // add rider to the downRiders vector
}

vector<Rider> Floor::removeUpRiders(int max) // int is max #of riders...max = #of unused spaces on elevator
{
  vector<Rider> removedRiders; // create an empty vector for riders to be removed
  
  if (hasUpRiders()) // if there are any up riders...
  {
    vector<Rider> remainingRiders; // create an empty vector for riders to remain on the floor

    for (unsigned int i = 0; i < upRiders.size(); i++) // traverse the upRiders vector
    {  
      if (max > removedRiders.size()) // if there are still spaces left on the elevator...
         removedRiders.push_back(upRiders[i]);  // add an upRider to the vector of riders to be removed
      else // else
         remainingRiders.push_back(upRiders[i]); // add an upRider to the vector of riders to remain on the floor
    }

    // replace the upRiders vector with the vector of remaining riders
    upRiders = remainingRiders;
  }

  // return the vector of removed riders
  return removedRiders;
}

vector<Rider> Floor::removeDownRiders(int max) // to move onto elevator
{
  // like removeUpRiders, but using the downRiders vector
  vector<Rider> removedRiders;
     
  if (hasDownRiders())
  {
     vector<Rider> remainingRiders;
     
     for (unsigned int i = 0; i < downRiders.size(); i++)
     {
       if (max > removedRiders.size())
         removedRiders.push_back(downRiders[i]);
       else
         remainingRiders.push_back(downRiders[i]);
     }
     
    downRiders = remainingRiders;
  }
     
  return removedRiders;
}

bool Floor::isPreferredDirectionUp() const // based on Rider with smallest ID
{
  // if there are no downRiders, return true
   if (!(hasDownRiders()))
     return true;
   
  // if there are no upRiders, return false
   else if (!(hasUpRiders()))
     return false;

  // if the ID of the first upRider (upRider[0]) is less than that of the first downRider...
   else if (upRiders[0] < downRiders[0])
     return true; // return true
   else
     return false; // return false
}

// friend function
ostream& operator<<(ostream& out, const Floor& f)
{
  out << "\nFloor: " << f.getName() << ", Location: " << f.getLocation() << ",  #'s of up riders: " << f.getUpRiderCount() << ", #'s of down riders: " << f.getDownRiderCount();
  return out;
}