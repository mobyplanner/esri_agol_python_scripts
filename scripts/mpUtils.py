import time, datetime
from arcgis.gis import GIS
from arcgis.apps import workforce

# Commandline arguments
def cliArguments(typology):
    import argparse
    parser = argparse.ArgumentParser(description= typology + ' Assignments on Workforce Project')
    # Generic commandline arguments
    parser.add_argument('-u', dest='username', help='AGOL username', required=True)
    parser.add_argument('-p', dest='password', help='AGOL password', required=True)
    # Workforce commandline arguments
    parser.add_argument('-pn', dest='projectName', help='Workforce project name', required=True)
    if typology == 'Bulk':
        parser.add_argument('-f', dest='xlsFile', help='XLS File to upload', required=True)
    elif typology == 'Plan':
        parser.add_argument('-dp', dest='day2Plan', help='day to plan (0 today, 1 tomorrow, 2 ...)', required=True)
        parser.add_argument('-sh', dest='routeStartHour', help='hour of starting service', required=True)
        parser.add_argument('-wh', dest='workingHours', help='working day duration [hours]', required=True)
        parser.add_argument('-ms', dest='maxStops', help='maximum stops per route', required=True)
        parser.add_argument('-st', dest='serviceTime', help='duration of service time [minutes]', required=True)
        parser.add_argument('-sp', dest='startingPoints', help='starting points feature layer name', required=True)
    args = parser.parse_args()
    return args

# AGOL authentication
def agolAuth(username, password):
    print('\nAuthenticating on your AGOL...')
    try:
        mpGis = GIS("https://www.arcgis.com", username=username, password=password)
    except:
        print()
        exit()
    print('Authentication Done!\n')
    print('AGOL urls -> ', str(mpGis))
    return mpGis

# Workforce project
def wkfProjectInfo(gisObj, projectName):
    try:
        mpWkfProjectItem = gisObj.content.search(query='title:"'+ projectName + '" type:Workforce Project')[0]
        mpWkfProjectId = mpWkfProjectItem.id
        mpWkfProject = workforce.Project(gisObj.content.get(mpWkfProjectId))
        print('\nGetting ' + str(mpWkfProject) + ' project info...')
    except:
        print()
        print('\nProject Name not found. Check workforce project name.')
        exit()
    print('Project ID --> ' + str(mpWkfProjectId))
    return mpWkfProjectId, mpWkfProject

# workforce dispatchers
def wkfDispatcherInfo(wkfProjectObj, username):
    mpWkfDispatchersList = wkfProjectObj.dispatchers.search()
    mpWkfDispatcher = wkfProjectObj.dispatchers.get(user_id=username)
    return mpWkfDispatchersList, mpWkfDispatcher

# workforce workers
def wkfWorkersInfo(wkfProjectObj):
    mpWkfWorkersList = wkfProjectObj.workers.search()
    mpWkfWorkersFset = wkfProjectObj.workers_layer.query()
    return mpWkfWorkersList, mpWkfWorkersFset

# workforce assigments
def wkfAssignmentsInfo(wkfProjectObj, wkfAssignmentsQuery='1=1'):
    mpWkfAssignmentsList = wkfProjectObj.assignments.search()
    mpWkfAssignmentsFset = wkfProjectObj.assignments_layer.query(where=wkfAssignmentsQuery)
    return mpWkfAssignmentsList, mpWkfAssignmentsFset

# UTC offset
def utcOffSet():
    ts = time.time()
    hereTime = datetime.datetime.fromtimestamp(ts)
    utcTime = datetime.datetime.utcfromtimestamp(ts)
    utcOffSet = (hereTime - utcTime).total_seconds()
    return utcOffSet



