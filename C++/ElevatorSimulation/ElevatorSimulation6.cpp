/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

#include <iostream>
using std::cin;
using std::cout;
using std::endl;

#include <cstdlib>
#include <ctime>
#include <cmath>

#include "Building.h"

int getArrivalsForThisSecond(double averageRiderArrivalRate)
{
  int arrivals = 0;
  double probOfnArrivals = exp(-averageRiderArrivalRate); // for n=0 -- requires cmath
  
  for(double randomValue = (rand() % 1000) / 1000.0; // requires cstdlib AND srand in main
    (randomValue -= probOfnArrivals) > 0.0;
    probOfnArrivals *= averageRiderArrivalRate / ++arrivals);
  
  return arrivals;
}

int main()
{
  srand(time(0)); rand(); // requires cstdlib and ctime
  Building building;

  // add one rider per second for 10 seconds
  for (int i = 0;;i++)
  {
    double AvgRiderRate = 0.7;

    if (!(i % 10) && i != 0)  // pause every 10 seconds
    {
      cout << "Press ENTER to continue, X-ENTER to quit...\n";
      if (cin.get() > 31) break;
    }
    cout << building.step(getArrivalsForThisSecond(AvgRiderRate)) << endl;
  }
  cout << "DONE: All riders should be gone, and all elevators idle\n";
}

