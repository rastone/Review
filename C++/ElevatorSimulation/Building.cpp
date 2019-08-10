/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

#include <iostream>
using std::cout;
using std::endl;
using std::ostream;

#include <vector>
using std::vector;

#include <cstdlib>
#include <ctime>

#include "Building.h"
#include "Floor.h"
#include "Elevator.h"
#include "Rider.h"

Building::Building()
{
  // Simulation timer initialized to zero
  simTime = 0;

  // create 5 floors
  floors.push_back(new Floor(0, "First Floor"));
  floors.push_back(new Floor(100, "Second Floor"));
  floors.push_back(new Floor(200, "Third Floor"));
  floors.push_back(new Floor(300, "Fourth Floor"));
  floors.push_back(new Floor(400, "Fifth Floor"));

  // create 2 elevators
  elevators.push_back(new Elevator(10, 85, *(floors[0])));
  elevators.push_back(new Elevator(10, 85, *(floors[1])));
  elevators.push_back(new Elevator(10, 85, *(floors[2])));
}

Building::~Building()
{
  // traverse floor vector and deallocate all floors
  for (int i = 0; i < getFloorCount(); i++)
  {
    delete floors[i];
  }

  // traverse elevator vector and deallocate all elevators
  for (int j = 0; j < getElevatorCount(); j++)
  {
    delete elevators[j];
  }
}

Building& Building::step(int nRidersToAdd)
{

  //******************************************************************************
  // the rider phase, you should see stranded riders randomly placed on floors,  *
  // and there should be no up-riders on the top floor and no down-riders on the *
  // bottom floor, and elevators should remain idle.                             *
  //******************************************************************************

  for (int i = 0; i < nRidersToAdd; i++)
  {
    int max = floors.size(); // max number of floors
    int from = 0;
    int to = 0;

    getDifferentInts(max, from, to); // create a rider with randomly selected from- and to-floors
    (*(floors[from])).addNewRider(Rider(*(floors[to]))); // tell the from-floor to add this rider
  }

  // increment timer once per second
  this->simTime++;

  //***************************************************************************************
  // the elevator phase, the elevators should (a) stop to pickup riders on the floors on  *
  // their way to another destination, and (b) go to floors with waiting riders after     *
  // they reach an idle state.                                                            *
  //***************************************************************************************

  // ELEVATOR ACTIONS [3]
  for (int i = 0; i < getElevatorCount(); i++) 
  {
    if (!elevators[i]->isDoorOpen()) // if elevator door is closed (move up or down) [3]
    {
      // if not near enough to destination to reach it in this time step, continue moving [3]
      if  (!elevators[i]->isNearDestination()) 
      {
        if (elevators[i]->isDirectionUp()) // if elevator direction is up, move up [3]
        {
          elevators[i]->moveUp();
        }
        else // otherwise, move down [3]
        {
          elevators[i]->moveDown();
        }
      }
      else // otherwise it's near enough to destination to reach it in this time step... [4]
      {
        elevators[i]->moveToDestinationFloor(); // tell elevator to move to its destination floor [4]
        elevators[i]->openDoor(); // tell elevator to open its door [4]
        elevators[i]->removeRidersForDestinationFloor(); // tell elevator to remove riders for its destination floor

        // get a non-const pointer to the elevator's destination floor (using const_cast) [5]
	Floor* elvDestinationFl = const_cast<Floor*>(&elevators[i]->getDestination());

        // if elevator is empty, choose a direction based on longest-waiting rider (the one with the smallest ID) on the floor: [5]
        if (elevators[i]->getRiderCount() == 0)
        {
          if (elvDestinationFl->isPreferredDirectionUp()) // if the floor's chosen direction is up [5]
          {
            elevators[i]->setDirectionUp(); // tell elevator to set its direction to up [5]
          }
          else // otherwise [5]
          {
            elevators[i]->setDirectionDown(); // tell elevator to set its direction to down [5]
          }
        }

        int n = elevators[i]->getAvailableSpace();

        // if there is space in the elevator after letting off riders, board new ones [6]
        if (n > 0)
        {
          if (elevators[i]->isDirectionUp()) // if elevator direction is up, board up-riders (if any)... [6]
          {
            elevators[i]->addRiders(elvDestinationFl->removeUpRiders(n));
          }
          else
          {
            elevators[i]->addRiders(elvDestinationFl->removeDownRiders(n)); // otherwise, board down-riders (if any) [6]
          }
        }
	
      // reassess elevator destination based on its riders [8]   
      elevators[i]->setDestinationBasedOnRiders();
			}
    } // End if door is closed
    else // otherwise if door is open (then it already let off riders, or is in its initial state) [7]
    {
      if (elevators[i]->getRiderCount() > 0) // if elevator has any riders [7]
      {
        elevators[i]->closeDoor(); // tell elevator to close its door [7]
      }
      else // otherwise [9]
      {
        elevators[i]->setIdle(); // tell elevator to go idle [9]
      }
    }
  } // End elevator loop

  //*********************************************************************************************************
  // the floor phase, the elevators should choose a direction, but do not move.                             *
  //*********************************************************************************************************

  // FLOOR ACTIONS [2]
  for (int i = 0; i < getFloorCount(); i++)
  {
    if (floors[i]->hasRidersWaiting()) // check each floor (for waiting riders) [2]
    {
      if(!floors[i]->hasRidersWaiting()) // if there are no riders waiting on this floor, continue with next floor [2]
      {
        continue;
      }
      for (int j = 0; j < getElevatorCount(); j++) // look at each elevator to see if it needs to be sent here [2]
      {
        // get elevator's relative location (negative if elevator is below floor) [2]
        int relativeLocation = elevators[j]->getLocation() - floors[i]->getLocation(); 

        if (elevators[j]->isIdle()) // if this elevator's idle... [2]
        {
          if (relativeLocation > 0) // if elevator is above the floor, set elevator direction to down [2]
          {
            elevators[j]->setDirectionDown();
          }
          else // otherwise if it's below, set elevator direction to up [2]
          {
            elevators[j]->setDirectionUp(); // tell elevator to close its door [2]
          }

          elevators[j]->setDestination(floors[i]); // set elevator's destination to this floor [2]
          elevators[j]->closeDoor(); // tell elevator to close its door [2]

        } // end idle

        // else if there are riders on this floor waiting to go up, and the elevator is going up... [10]
	else if (floors[i]->hasUpRiders() && elevators[j]->isDirectionUp())
        {
          // get distance from elevator's destination floor to this floor (positive if elevator destination is above this floor) [10]
          int distFromElvDestination = elevators[j]->getDestination().getLocation() - floors[i]->getLocation();

          // if elevator is below floor and elevator destination is above this floor [10]
          if (elevators[j]->getLocation() < floors[i]->getLocation() && distFromElvDestination > 0) 
          {
          // set elevator's destination to this floor [10]
          elevators[j]->setDestination(floors[i]);
          }
        }

        // else if there are riders on this floor waiting to go down, and the elevator is going down... [10]
        else if (floors[i]->hasDownRiders() && elevators[j]->isDirectionDown())
        {
          // get distance from elevator's destination floor to this floor (positive if elevator destination is above this floor) [10]
          double distFromElvDestination = elevators[j]->getDestination().getLocation() - floors[i]->getLocation();

          // if elevator is above floor and elevator destination is below this floor [10]
          if (elevators[j]->getLocation() > floors[i]->getLocation() && distFromElvDestination < 0) 
          {
            // set elevator's destination to this floor [10]
            elevators[j]->setDestination(floors[i]);
          }
        }

      } // End elevator loop
    } // End riders waiting
  } // End floor loop

  return *this;

} // end Building::step

void Building::getDifferentInts(int max, int& a, int& b)
{
  do
  {
    a = rand() % max; // range is 0 to (max-1)
    b = rand() % max; // range is 0 to (max-1)
  } while (a == b); // try again if they are the same
}

ostream& operator<<(ostream& out, const Building& b)
{
  // print the time
  for (int i = 0; i < 1; i++) 
  {
    out << "Time: " << b.simTime << endl;
  }

  // print the elevators
  for (int i = 0; i < b.getElevatorCount(); i++)
    out << "Elevator " << i << ": " << b.getElevator(i);

  // print the floors with waiting riders
  for (int i = 0; i < b.getFloorCount(); i++)
  {
    if (b.getFloor(i).hasRidersWaiting())
      out << b.getFloor(i);
  }

  out << endl;

  return out;
}