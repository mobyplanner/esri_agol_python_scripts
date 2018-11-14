import time, datetime
import pandas as pd
from arcgis.gis import GIS
from arcgis.apps import workforce
import arcgis.features as gisFeatures

import mpUtils

# Commandline arguments
args = mpUtils.cliArguments('Plan')

# AGOL authentication
mpGis = mpUtils.agolAuth(args.username, args.password)
# Workforce project infos
mpWkfProjectId, mpWkfProject = mpUtils.wkfProjectInfo(mpGis, args.projectName)
# Workforce dispatchers
mpWkfDispatchersList, mpWkfDispatcher = mpUtils.wkfDispatcherInfo(mpWkfProject, args.username)
# Workforce assigments
mpWkfAssignmentsQuery = 'status = 0'
mpWkfAssignmentsList, mpWkfAssignmentsFset = mpUtils.wkfAssignmentsInfo(mpWkfProject, mpWkfAssignmentsQuery)
# Workforce workers
mpWkfWorkersList, mpWkfWorkersFset = mpUtils.wkfWorkersInfo(mpWkfProject)

# Planner initialization
mpTravelMode = 'Driving'
mpStartingPoints = mpGis.content.search(query='title:' + args.startingPoints, item_type='Feature Layer')[0]
mpToday = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
mpRouteStartTime = mpToday + datetime.timedelta(days=int(args.day2Plan), hours=int(args.routeStartHour))

# Check if there are unassigned events
if len(mpWkfAssignmentsFset) == 0:
    print('All events are assigned on ' + str(mpWkfProject))
    exit()

# Planning
print("\nStart planning...")
print("number of workers -> " + str(len(mpWkfWorkersList)))
start_execution = time.time()
mpPlanRoutesResult = gisFeatures.analysis.plan_routes(mpWkfAssignmentsFset.to_dict(), 
                                                      route_count = len(mpWkfWorkersList), # n. of workers
                                                      max_stops_per_route = args.maxStops,
                                                      stop_service_time = args.serviceTime,
                                                      route_start_time = (mpRouteStartTime).timestamp()*1000, # [ms]
                                                      start_layer = mpStartingPoints,
                                                      return_to_start = True,
                                                      travel_mode=mpTravelMode,
                                                      max_route_time = int(args.workingHours)*60 # accumulation of travel time and the total service time at visited stops (minutes)
                                                     )
print("Planning completed in %s minutes.\n" % str(round(((time.time() - start_execution))/60, 2)))

# df from plan_routes with attributes
mpRoutesStopsAttributesDf = pd.DataFrame.from_records([i['attributes'] for i in 
                                mpPlanRoutesResult['assigned_stops_layer'].layer.featureSet.features])
# df from plan_routes with geometry
mpRoutesStopsGeometryDf = pd.DataFrame.from_records([i['geometry'] for i in 
                                mpPlanRoutesResult['assigned_stops_layer'].layer.featureSet.features])
# df merge with all planned details
mpRoutesStopsDf = mpRoutesStopsAttributesDf.merge(mpRoutesStopsGeometryDf, left_index=True, right_index=True)

if len(mpPlanRoutesResult['unassigned_stops_layer'].layer) == 0:
    unassignedStops = 0
else:
    unassignedStops = len(mpPlanRoutesResult['unassigned_stops_layer'].layer.featureSet.features)

print('Planned: ' + str(len(mpPlanRoutesResult['assigned_stops_layer'].layer.featureSet.features)-len(mpWkfWorkersList)*2) + ' Unplanned: ' + str(unassignedStops))

# Dataframe RouteName Vs userId
mpRouteNameDf = pd.DataFrame(mpRoutesStopsDf.RouteName.unique(), columns=['RouteName'])
mpWkfWorkersDf = mpWkfWorkersFset.sdf
mpRouteNameVsWorkersDf = pd.merge(mpRouteNameDf, mpWkfWorkersDf[['OBJECTID', 'userId']], left_index=True, right_index=True)

# Assign events to feature service
start_execution = time.time()
mpWkfFeaturesOriginal = mpWkfAssignmentsFset.features
mpWkfFeatures2Update = []
for mpWoidList in mpRoutesStopsDf[mpRoutesStopsDf.StopType == 'Stop'].workOrderId: # for every GlobaID found in route_plans output
    mpGetRouteName = mpRoutesStopsDf[mpRoutesStopsDf.workOrderId == mpWoidList].RouteName.iloc[0]
    mpConvertToWorker = mpRouteNameVsWorkersDf[mpRouteNameVsWorkersDf.RouteName == mpGetRouteName]
    mpWorkerObjectId = mpConvertToWorker.OBJECTID.values[0]
    
    mpWkfAssignment2Set = [elem for elem in mpWkfFeaturesOriginal if elem.attributes['workOrderId'] == mpWoidList][0] #
    mpWkfAssignment2Set.attributes['status'] = 1
    mpWkfAssignment2Set.attributes['dueDate'] = datetime.datetime.fromtimestamp(mpRoutesStopsDf[mpRoutesStopsDf.workOrderId == mpWoidList].ArriveTime/1000)
    mpWkfAssignment2Set.attributes['workerId'] = mpWorkerObjectId
    mpWkfAssignment2Set.attributes['assignedDate'] = datetime.datetime.now()
    mpWkfAssignment2Set.attributes['EditDate'] = datetime.datetime.now()
    mpWkfAssignment2Set.attributes['Editor'] = mpWkfDispatcher.object_id
    
    mpWkfFeatures2Update.append(mpWkfAssignment2Set)

mpWkfProject.assignments_layer.edit_features(updates=mpWkfFeatures2Update)
print("Assignments on workforce " + str(mpWkfProject) + " completed in %s minutes.\n" % str(round(((time.time() - start_execution))/60, 2)))


