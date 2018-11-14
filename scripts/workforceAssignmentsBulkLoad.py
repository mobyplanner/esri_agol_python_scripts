import time, datetime
import pandas as pd
from arcgis.gis import GIS
from arcgis.apps import workforce

import mpUtils

# Commandline arguments
args = mpUtils.cliArguments('Bulk')

# AGOL authentication
mpGis = mpUtils.agolAuth(args.username, args.password)
# Workforce project infos
mpWkfProjectId, mpWkfProject = mpUtils.wkfProjectInfo(mpGis, args.projectName)
# Workforce dispatchers
mpWkfDispatchersList, mpWkfDispatcher = mpUtils.wkfDispatcherInfo(mpWkfProject, args.username)
# Workforce assigments
mpWkfAssignmentsList, mpWkfAssignmentsFset = mpUtils.wkfAssignmentsInfo(mpWkfProject)

assignmentsNumber = len(mpWkfAssignmentsList)
if assignmentsNumber != 0:
    print("\nThere are " + str(assignmentsNumber) + " events on " + str(mpWkfProject) + " project.")
    mpContinue = None
    while True:
        defaultYes = 'y'
        mpContinue = input("Do you want to delete all events before upload? ([y]/n/q) ") or defaultYes
        if mpContinue not in ('y', 'n', 'q'):
            print("Not an appropriate choice. Please select 'y' or 'n'")
        if mpContinue == 'n':
            break
        if mpContinue == 'q':
            print('Program end.')
            exit()
        if mpContinue == 'y':
            print('Cleaning...')
            mpWkfProject.assignments.batch_delete(mpWkfProject.assignments.search()) # delete all assignements before reassigments
            break

# Read file
myBulkDf = pd.read_excel(args.xlsFile)
print("Loading " + str(myBulkDf.shape[0]) + " events...")

# loads myBulkDf into assignments feature layer
start_execution = time.time()
for i in myBulkDf.index:
    readRows = myBulkDf.loc[i]
    mpWkfProject.assignments.add(
        dispatcher=mpWkfDispatcher,
        description=readRows.eventName,
        work_order_id=readRows.eventID,
        location=readRows.eventAddress,
        assignment_type=mpWkfProject.assignment_types.get(name=readRows.eventType),
        status=0, # 0->Unassigned, 1-> Assigned
        priority=int(readRows.eventPriority),  # range must be 0-4
        geometry=dict(x=float(readRows.Longitude), 
                      y=float(readRows.Latitude),
                      spatialReference=dict(wkid=int(4326))
                     )
    )
    print('--> ' + str(readRows.eventID) + ' added')
print("Bulk completed in %s minutes.\n" % str(round(((time.time() - start_execution))/60, 2))) 