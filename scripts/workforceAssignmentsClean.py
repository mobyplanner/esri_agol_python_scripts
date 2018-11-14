import time, datetime
import pandas as pd
from arcgis.gis import GIS
from arcgis.apps import workforce

import mpUtils

# Commandline arguments
args = mpUtils.cliArguments('Clean')

# AGOL authentication
mpGis = mpUtils.agolAuth(args.username, args.password)
# Workforce project infos
mpWkfProjectId, mpWkfProject = mpUtils.wkfProjectInfo(mpGis, args.projectName)
# Workforce assigments
mpWkfAssignmentsList, mpWkfAssignmentsFset = mpUtils.wkfAssignmentsInfo(mpWkfProject)

mpWkfAssignmentsDf = mpWkfAssignmentsFset.sdf
mpWkfAssignmentsNumber = mpWkfAssignmentsDf[mpWkfAssignmentsDf.status == 1].shape[0]
if mpWkfAssignmentsNumber == 0:
    print('No assignment found.')
    exit()
print("\nWill be clean " + str(mpWkfAssignmentsNumber) + " assignements on " + str(mpWkfProject) +".")

mpContinue = None
while True:
    defaultYes = 'y'
    mpContinue = input("Do you want to proceed? ([y]/n) ") or defaultYes
    if mpContinue not in ('y', 'n'):
        print("Not an appropriate choice. Please select 'y' or 'n'")
    if mpContinue == 'n':
        print('Clean aborted.')
        exit()
    if mpContinue == 'y':
        break

start_execution = time.time()
mpWkfFeaturesOriginal = mpWkfAssignmentsFset.features
mpWkfFeatures2Update = []
for mpGidList in mpWkfAssignmentsDf.GlobalID:
    mpWkfAssignment2Reset = [elem for elem in mpWkfFeaturesOriginal if elem.attributes['GlobalID'] == mpGidList][0]
    mpWkfAssignment2Reset.attributes['status'] = 0 
    mpWkfAssignment2Reset.attributes['dueDate'] = None
    mpWkfAssignment2Reset.attributes['workerId'] = None
    mpWkfAssignment2Reset.attributes['assignedDate'] = None
    mpWkfAssignment2Reset.attributes['EditDate'] = None
    mpWkfAssignment2Reset.attributes['Editor'] = None
    
    mpWkfFeatures2Update.append(mpWkfAssignment2Reset)
    
mpWkfProject.assignments_layer.edit_features(updates=mpWkfFeatures2Update)
print("Cleaning completed in %s minutes.\n" % str(round(((time.time() - start_execution))/60, 2)))
