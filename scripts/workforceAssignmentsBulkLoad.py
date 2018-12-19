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
    print("\nThere are " + str(assignmentsNumber) + " tasks on " + str(mpWkfProject) + " project.")
    mpContinue = None
    while True:
        defaultYes = 'y'
        mpContinue = input("Do you want to delete all tasks before upload? ([y]/n/q) ") or defaultYes
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
print("Loading " + str(myBulkDf.shape[0]) + " tasks...")

# loads myBulkDf into assignments feature layer
start_execution = time.time()
mpWkfFeatures2Upload = []
for _, row in myBulkDf.iterrows():
    mpWkfFeatures2Upload.append(
        workforce.Assignment(
            mpWkfProject,
            dispatcher=mpWkfDispatcher,
            description=row.eventName,
            work_order_id=row.eventID,
            location=row.eventAddress,
            assignment_type=mpWkfProject.assignment_types.get(name=row.eventType),
            status="Unassigned",
            priority=int(row.eventPriority),
            geometry=dict(x=float(row.Longitude), 
                          y=float(row.Latitude), 
                          spatialReference=dict(wkid=int(4326))
                          )
        )
    )
mpWkfProject.assignments.batch_add(mpWkfFeatures2Upload)
print("--- %s tasks loaded in %s minutes ---" % (len(mpWkfFeatures2Upload), str(round(((time.time() - start_execution))/60, 2))))