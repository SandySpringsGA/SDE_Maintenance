#################################################################################################################################
#                                                                                                                               #
#                                                      SDE MAINTENENACE                                                         #
#                                                RECONCILE, POST && COMPRESS                                                    #
#                                                                                                                               #
#################################################################################################################################
	
# coding: utf-8

#################################################################################################################################
#                                                                                                                               #
#                     *Recommended*: Run the "SDE Version Diagnostics" script before running this script.                       #
#                 This will check for inconsistencies in the delta (A and D) tables of a versioned geodatabase                  #
#                                                                                                                               #
#################################################################################################################################


# ================================================================================================================================


##################################################################################################################################

#                                                        IMPORT MODULES:

import datetime # Necessary: to get the current date for creating files/logs/directories/etc
import arcpy    # Essential: to run any of the esri functions/methods called within this script
import time     # Optional:  to run the time.sleep method
import os       # Necessary: to run any of the file I/O methods && for creating a new directory for the Logs

#################################################################################################################################

#                                            DEFINE FILEPATH/CONNECTION VARIABLES:
#                                    database/server/filepaths removed for security reasons

# connection path for the database, change this variable to perform maintenance on a different database
# current path is for the 'REDACTED' instance, 'REDACTED' database  
db = "REDACTED"

# filepath where a directory will be created for the current maintenance task(s)
SDE_maintenance_folderPath = "REDACTED"

#################################################################################################################################

#                                                  DATE HANDLING/FORMATTING:

today = datetime.date.today() # method to get the current date, assigning it to the variable "today"

day = today.day               # assigns the day portion of today's date to the "day" variable
month = today.month           # assigns the month portion of today's date to the "month" variable
year = today.year             # assigns the year portion of today's date to the "year" variable

dayString = ''                # creates an empty String variable for the day that will be used later
monthString = ''              # creates an empty String variable for the day that will be used later
yearString = str(year)        # casts the year variable from int to String and assigns it to the "yearString" variable


# Functions to encapsulate the methods to check if the day/month portions of the date are less than 10.  
# These don't have to be encapsulated in functions, but it is a better practice from an OOP standpoint

# the day and dayString variables get passed into the function
def checkDayLength(day, dayString): 
     # if the day of the month is less than 10 -->
	if(int(day) < 10):  
         # then a leading "0" gets assigned to the "dayString" variable
		dayString = "0"  
        # then the day of the month is appended, useful for making 1 into 01 which is more human-readable in a file name
		dayString = dayString + (str(day))  
     # otherwise, the two-digit day gets cast from an int to a String, then is assigned to the "dayString" variable
	else: dayString = str(day)

	return dayString  # returns the "dayString" variable back to the method that called it


# the month and monthString variables get passed into the function
def checkMonthLength(month, monthString):
     # if the month number is less than 10 -->
	if(int(month) < 10):
         # then a leading "0" gets assigned to the "monthString" variable
		monthString = "0"
         # then the month number is appended, useful for making 1 into 01 which is more human-readable in a file name
		monthString = monthString + (str(month))
     # otherwise, the two-digit month number gets cast from an int to a String, then is assigned to the "monthString" variable
	else: monthString = str(month)

	return monthString  # returns the "monthString" variable back to the method that called it


# Function/method calls to transform the current date into a human readable date format for use in file(path) names
dayString = checkDayLength(day, dayString)          # this calls the above defined "checkDayLength" function
monthString = checkMonthLength(month, monthString)  # this calls the above defined "checkMonthLength" function 

################################################################################################################################

#                                    DEFINE VARIABLES THAT ARE DEPENDENT ON THE DATE FUNCTIONS:

# Variable to concatenate the String versions of the "day" "month" and "year" variable into the folowing format: YYYYMMDD
todayString = yearString + monthString + dayString

# Variable for the file path where all logs and other files will be stored for this maintenance period
currentFolderPath = SDE_maintenance_folderPath + "_Update" + todayString

# Reconcile & Post Log file name 
reconcileFileName = currentFolderPath + "//Reconcile_Log.txt"

################################################################################################################################

#                                                     PRE-MAINTENANCE CHECKS:

# method to return a tuple of all currently connected DB users; tuple is assigned to the "userList" variable
userList = arcpy.ListUsers(db) # "db" variable defined in line *31* above

# creates a file object for file I/O, with the name: "UserList_beforeEditSession.txt" within the 
# 	current maintenance period folder.  File is opened in write ('w') mode
file = open(os.path.join(currentFolderPath, "UserList_beforeEditSession.txt"), 'w')

# loop to iterate over each item in the 'userList" tuple
for i in userList:
     # take each item in the tuple, cast it to a String, then write it to the .txt file object created in the previous step
	file.write(''.join(str(s) for s in i) + '\n')

# method to close the file which saves the file and also prevents the file object from persisting in system memory
file.close()


# method to prevent any additional connections to the DB
arcpy.AcceptConnections(db, False)

# optional method to wait 15 minutes after blocking all new connections
    # this method can be used if you want to send out notifications to users that are still connected to save, log-off, etc.
time.sleep(900) 

################################################################################################################################

#                                        ACTUAL DATABASE MAINTENANCE ACTIVITY BEGINS HERE:

# ****************************************************************************************************************************

#                      INSERT METHOD HERE TO CALL THE BATCH SCRIPT TO STOP THE SERVICE FOR ARCGIS SERVER

# ****************************************************************************************************************************



###############################################################################################################################

#                                                       DISCONNECT USERS:

# method to disconnect all SDE users
arcpy.DisconnectUser(db, 'ALL')

# optional method to list all db users again after the DisconnectUser method (to make sure all users were indeed disconnected)
userList1 = arcpy.ListUsers(db)

#prints the above "userList1" variable to the system console
print(userList1)

################################################################################################################################

#                                                   LOG CURRENT DB VERSIONS:

# gets a tuple of all current DB versions and assigns the tuple to the "versionList" variable
versionList = arcpy.ListVersions(db)

# creates a file object for file I/O, with the name: "VersionList_beforeEditSession.txt" within the 
#  current maintenance period folder.  File is opened in write ('w') mode
file = open(os.path.join(currentFolderPath, "VersionList_beforeEditSession.txt"), 'w')

# loop to iterate over each item in the 'VersionList" tuple
for i in versionList:
     # take each item in the tuple, cast it to a String, then write it to the .txt file defined created in the previous step
	file.write(''.join(str(s) for s in i) + '\n')

    # method to close the file which saves the file and also prevents the file object from persisting in system memory
file.close()

################################################################################################################################

#                                                   RECONCILE & POST VERSIONS:

# method to Reconcile && Post && Delete all child versions up to DEFAULT
arcpy.ReconcileVersions_management(db, "ALL_VERSIONS", "dbo.DEFAULT", versionList, "LOCK_ACQUIRED", 
                                   "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_TARGET_VERSION","POST", 
                                   "DELETE_VERSION", reconcileFileName)

# NOTE: this method will also DELTE all child versions

################################################################################################################################

#                                                         DB COMPRESS:

# Run the compress tool. 
arcpy.Compress_management(db)

# Rebuild indexes and analyze the states and states_lineages system tables
arcpy.RebuildIndexes_management(db, "SYSTEM", "", "ALL")

################################################################################################################################

#                                                   ANALYZE  SYSTEM  TABLES:

# method to analyze the states and states_lineages system tables
arcpy.AnalyzeDatasets_management(db, "SYSTEM", "", "ANALYZE_BASE", "ANALYZE_DELTA", "ANALYZE_ARCHIVE")

################################################################################################################################                       

#                                          ALLOW NEW CONNECTIONS TO THE DATABASE:

arcpy.AcceptConnections(db, True)

################################################################################################################################ 

#                                               RE-CREATE ALL USER VERSIONS:

# Set local variables
parentVersion    = "dbo.QC"
versionName      = "QC"
accessPermission = "PROTECTED"

# creates a QC version w/ parent version= 'DEFAULT'  # all user versions have parent version= 'QC'
arcpy.CreateVersion_management(db, "dbo.DEFAULT", versionName, "PUBLIC")

# loop to iterate over each user in the userList tuple & recreate that version
for i in versionList:  # "versionList" variable defined in line *156* above
	
	 # if statement to find all named (user) versions
    if(str(versionList[i]) != "dbo.DEFAULT" and str(versionList[i]) != "DBO.QC"):
        versionName = str(versionList[i])
        arcpy.CreateVersion_management(db, parentVersion, versionName, accessPermission)
        
    else: continue # this will skip over the "dbo.DEFAULT" & "DBO.QC" items in the versionList tuple

################################################################################################################################

#                                         LOG DB VERSIONS AFTER DB MAINTENANCE:

# list all current versions, assigne to new "versionList2" varaiable
versionList2 = arcpy.ListVersions(db)

# creates a file object for file I/O, with the name: "VersionList_AfterEditSession.txt" within the 
#  current maintenance period folder.  File is opened in write ('w') mode
file = open(os.path.join(currentFolderPath, "VersionList_AfterEditSession.txt"), 'w')

# loop to iterate over each item in the 'VersionList2" tuple
for i in versionList2:
     # take each item in the tuple, cast it to a String, then write it to the .txt file defined created in the previous step
    file.write(''.join(str(s) for s in i) + '\n')

# method to close the file which saves the file and also prevents the file object from persisting in system memory
file.close()


################################################################################################################################
#                                                                                                                              #
#                                                     *** THE END ***                                                          #
#                                                                                                                              #
################################################################################################################################


#================================================================================================================================


################################################################################################################################
#                                                                                                                              #
#                                                 * STILL NEED TO ADD: *                                                       #
#                                                                                                                              #
#    > Exception handling (try, except --> write to errorLog.txt file for any errors)                                          #
#                                                                                                                              #
#                                                                                                                              #
################################################################################################################################

