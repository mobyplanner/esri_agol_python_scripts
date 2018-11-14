## Workforce Plan Assignments
This script determines how to efficiently divide tasks among a workers considering workers number in the Esri Workforce project and plan optimized daily initeraries based on starting points, max stops, service time duration and travel time.

The script specific arguments are as follows:
- -u \<userName\> -> AGOL username
- -p \<password\> -> AGOL password
- -pn \<projectName\> -> Workforce project name
- -dp \<day2plan\> -> day to plan (0 today, 1 tomorrow, 2 ...)
-  -sh \<routeStarthour\> -> hour of starting service (8, 9, ... , 12, 13, ...)
-  -wh \<workingHours\> -> working day duration [hours]
-  -ms \<maxStops\> -> maximum stops per route
-  -st \<serviceTime\> -> duration of service time [minutes]
-  -sp \<startingpoints\> -> starting points feature layer name
- -h -> show this help

#### Example usage:
```python
python workforceAssignmentsPlan.py -u 'username' -p 'password' -pn 'projectName' -dp 1 -sh 8 -wh 8 -ms 3 -st 10 -sp 'myStartingPoints'
```

#### Requirements:
- Esri Workforce project w/ workers, tasks and assignments type
- A feature layer containing starting points (see ../sampleData/workforceStartingPoints.xlsx for easy upload)


#### What it does
 1. First the script uses the provided credentials to authenticate with AGOL
 2. Then is determined workforce Project ID based on Project Name
 3. Next query unassigned tasks and get infos about staring points
 4. Call Esri Plan Routes Task on AGOL
 5. Based on plan_routes the results assign the tasks to workers with due date and time