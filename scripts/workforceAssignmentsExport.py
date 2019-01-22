import time, datetime
import pandas as pd
from arcgis.gis import GIS
from arcgis.apps import workforce

import mpUtils

# Commandline arguments
args = mpUtils.cliArguments('Export')

# AGOL authentication
mpGis = mpUtils.agolAuth(args.username, args.password)
# Workforce project infos
mpWkfProjectId, mpWkfProject = mpUtils.wkfProjectInfo(mpGis, args.projectName)
# Workforce dispatchers
mpWkfDispatchersList, mpWkfDispatcher = mpUtils.wkfDispatcherInfo(mpWkfProject, args.username)
# Workforce assigments
mpWkfAssignmentsList, mpWkfAssignmentsFset = mpUtils.wkfAssignmentsInfo(mpWkfProject)
# Workforce workers
mpWkfWorkersList, mpWkfWorkersFset = mpUtils.wkfWorkersInfo(mpWkfProject)

mpWkfAssignmentsDf = mpWkfAssignmentsFset.sdf

# Map values
boolType = {0:'No', 1: 'Yes'}
assignmentTypeMap = {}
for atm in mpWkfProject.assignment_types.search():
    assignmentTypeMap[atm.code] = atm.name
statusMap = {0:'Unassigned',
             1:'Assigned',
             2:'In progress',
             3:'Completed',
             4:'Declined',
             5:'Paused',
             6:'Canceled'}
priorityMap = {0:'None',
               1:'Low',
               2:'Medium',
               3:'High',
               4:'Critical'}
workersMap = {}
for wm in mpWkfWorkersList:
    workersMap[wm.id] = wm.name
mpWkfAssignmentsDf.assignmentRead = mpWkfAssignmentsDf.assignmentRead.map(boolType)
mpWkfAssignmentsDf.assignmentType = mpWkfAssignmentsDf.assignmentType.map(assignmentTypeMap)
mpWkfAssignmentsDf.status = mpWkfAssignmentsDf.status.map(statusMap)
mpWkfAssignmentsDf.priority = mpWkfAssignmentsDf.priority.map(priorityMap)
mpWkfAssignmentsDf.workerId = mpWkfAssignmentsDf.workerId.map(workersMap)

# datetime conversion
columnsWithDateTime = mpWkfAssignmentsDf.select_dtypes(include='datetime64[ns]').columns
mpWkfAssignmentsDf[columnsWithDateTime] = mpWkfAssignmentsDf[columnsWithDateTime].astype('int64')
mpWkfAssignmentsDf[columnsWithDateTime] = ((mpWkfAssignmentsDf[columnsWithDateTime] + mpUtils.utcOffSet()*pow(10,9))) # add utcOffset to epoch
mpWkfAssignmentsDf[columnsWithDateTime] = mpWkfAssignmentsDf[columnsWithDateTime].where(mpWkfAssignmentsDf[columnsWithDateTime] > (3.6*pow(10,12)), None) # NaT on old epoch
mpWkfAssignmentsDf[columnsWithDateTime] = mpWkfAssignmentsDf[columnsWithDateTime].astype('datetime64[ns]')

# DataFrame columns selection
mpWkfAssignments4xlsx = mpWkfAssignmentsDf[['OBJECTID', 'workOrderId', 'description', 'priority', 'assignmentType', 'status', 'workerId', 'dueDate', 'location', 'notes', 'assignedDate', 'assignmentRead', 'pausedDate', 'inProgressDate', 'completedDate', 'declinedDate', 'declinedComment']]
mpWkfAssignments4xlsx.rename(columns={'OBJECTID': 'Object ID', 'workOrderId': 'Work Order ID', 'description': 'Description', 'priority': 'Priority', 'assignmentType': 'Assignment Type', 'status': 'Status', 'workerId': 'Worker Name', 'dueDate': 'Due Date', 'location': 'Location', 'notes': 'Notes', 'assignedDate': 'Assigned date', 'assignmentRead': 'Assignment Read', 'pausedDate': 'Paused Date', 'inProgressDate': 'In Progress date', 'completedDate': 'Completed on', 'declinedDate': 'Declined on', 'declinedComment': 'Declined Comment'}, inplace=True)

# Xlsx export
start_execution = time.time()
now = datetime.datetime.now()
xlsOutputName = str(mpWkfProject) + '_assignments_' + str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + '.xlsx'
writer = pd.ExcelWriter(xlsOutputName, engine='xlsxwriter')
mpWkfAssignments4xlsx.to_excel(writer, sheet_name= str(mpWkfProject) + ' Assignments Output', index=False)
writer.save()
print("Assignments export " + str(mpWkfProject) + " completed in %s minutes.\n" % str(round(((time.time() - start_execution))/60, 2)))
