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

#                                                         BEGIN SCRIPT:

print("Staring script...\n....\n ")

##################################################################################################################################

#                                                        IMPORT MODULES:

print("Importing modules...")

script_start_time = None
script_ended_time = None
script_fails_time = None
tz = None

try:

    import datetime # Necessary: to get the current date for creating files/logs/directories/etc
    import pytz     # Necessary: to populate the time component of the datetime variable with correct timezone info, default == UTC-0

    tz = pytz.timezone('America/New_York')
    script_start_time = datetime.datetime.now(tz=tz) # date/time script started (will be a few ms behind, b/c of module imports)

    import arcpy    # Essential: to run any of the esri functions/methods called within this script
    import time     # Optional:  to run the time.sleep method
    import os       # Necessary: to run any of the file I/O methods && for creating a new directory for the Logs

    from subprocess import Popen # Necessary: to run the method call to run external batch files

    print("...module imports complete!\n ")

except ImportError as E:
    print(E)

#################################################################################################################################

#                                            DEFINE FILEPATH/CONNECTION VARIABLES:
#                                    database/server/filepaths removed for security reasons

print("Defining SDE Connection File...")

# connection path for the database, change this variable to perform maintenance on a different database
# current path is for the 'REDACTED' instance, 'REDACTED' database  
db = "INSERT_YOUR_SDE_CONNECTION_FILE_FILEPATH_HERE" #format = r'filepath'

print("...done defining SDE Connection File!\n ")

print("Defining FilePath for SDE Maintenance Output files...")

# filepath where a directory will be created for the current maintenance task(s)
SDE_maintenance_folderPath = "INSERT_FILEPATH_WHERE_YOU_WANT_ALL_OUTPUTS_STORED_HERE" #format = r'filepath'

print("...done defining FILEPATH variables!\n ")

print("Assigning maintenance variables...")

section_success = False
overall_success = False

def section_success_str(b):
    if(b):
        return "SUCCESS!"
    else: 
        return "failure!"

def overall_success_str(b):
    if(b):
        return "SUCCESS!"
    else: 
        return "failure!"

print("...done assigning maintenance variables!\n ")

#################################################################################################################################

#                                                  DATE HANDLING/FORMATTING:

print("Assigning date/time variables...")

today = datetime.date.today() # method to get the current date, assigning it to the variable "today"

day   = today.day             # assigns the day portion of today's date to the "day" variable
month = today.month           # assigns the month portion of today's date to the "month" variable
year  = today.year            # assigns the year portion of today's date to the "year" variable

dayString   = ''              # creates an empty String variable for the day that will be used later
monthString = ''              # creates an empty String variable for the day that will be used later
yearString  = str(year)       # casts the year variable from int to String and assigns it to the "yearString" variable


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

print("....\n ")

# Function/method calls to transform the current date into a human readable date format for use in file(path) names
dayString = checkDayLength(day, dayString)          # this calls the above defined "checkDayLength" function
monthString = checkMonthLength(month, monthString)  # this calls the above defined "checkMonthLength" function 

print("....done assigning date/time variables!\n ")

################################################################################################################################

#                                    DEFINE VARIABLES THAT ARE DEPENDENT ON THE DATE FUNCTIONS:

print("Making directory for logs...")

# Variable to concatenate the String versions of the "day" "month" and "year" variable into the folowing format: YYYYMMDD
todayString = yearString + monthString + dayString

os.mkdir(os.path.join(SDE_maintenance_folderPath, "Update_" + todayString))

# Variable for the file path where all logs and other files will be stored for this maintenance period
currentFolderPath = SDE_maintenance_folderPath + "/Update_" + todayString

# Maintenance Summary Log file name:
maintenance_summary_FileName = currentFolderPath + "//MaintenanceSummary_Log.txt"

error_Log_FileName = currentFolderPath + "//Error_Log.txt"

# Reconcile & Post Log file name 
reconcileFileName = currentFolderPath + "//Reconcile_Log.txt"

print("...done making directory for logs!\n ")

################################################################################################################################

#                                                MAINTENANCE & ERROR LOG CREATION:

print("Creating 'Maintenance Summary' file...")

#Create file for maintenance summary:
maintenance_summary = open(maintenance_summary_FileName, x)

print("...'Maintenance Summary' file created!\n ")


print("Writing template text to 'Maintenance Summary' file...")

# Boiler plate text to add to top of maintenance_summary file
boilerPlate = ('********************SDE MAINTENANCE LOG:********************\n '
              f'\nSDE Maintenance started: {script_start_time.time()} on: {script_start_time.date()} \n '
               '\nMaintenance  Activities:\n '
               '\nImport relevant modules: SUCCESS!'
               '\nAssign script variables: SUCCESS!'
               '\nCreate output directory: SUCCESS!'
               '\nDefine fileNames 4 logs: SUCCESS!')

#write boiler plate to maintenance_summary file
maintenance_summary.write(boilerPlate)

print("...done writing template text to 'Maintenance Summary' file!\n ")

#close the file
maintenance_summary.close()

print("Creating 'Error Log' file...")

#Create file for Error_Log:
error_Log = open(error_Log_FileName, x)

print("...'Error Log' file created!\n ")


print("Writing template text to 'Error Log' file...")

# Boiler plate text to add to top of Error_Log file
boilerPlate = '********************ERROR LOG:********************\n \n '

#write boiler plate to Error_Log file
maintenance_summary.write(boilerPlate)

print("...done writing template text to 'Error Log' file!\n ")

#close the file
maintenance_summary.close()

################################################################################################################################

#                                                     PRE-MAINTENANCE CHECKS:

print("Getting list of connected users...")

# method to return a tuple of all currently connected DB users; tuple is assigned to the "userList" variable
userList = arcpy.ListUsers(db) # "db" variable defined in line *31* above

print("...done getting list of connected users!\n ")


print("Writing list of users to .txt file...")

# creates a file object for file I/O, with the name: "UserList_beforeEditSession.txt" within the 
# 	current maintenance period folder.  File is opened in write ('w') mode
file = open(os.path.join(currentFolderPath, "UserList_beforeEditSession.txt"), 'w')

# loop to iterate over each item in the 'userList" tuple
for i in userList:
     # take each item in the tuple, cast it to a String, then write it to the .txt file object created in the previous step
	file.write(''.join(str(s) for s in i) + '\n')

# method to close the file which saves the file and also prevents the file object from persisting in system memory
file.close()

print("...done writing list of users to .txt file!\n ")


print("Blocking new connections to database...")

# method to prevent any additional connections to the DB
arcpy.AcceptConnections(db, False)

print("...done blocking new connections to database!\n ")


print("Wating 15 minutes to allow time for currently connected users to save and log off...")

# optional method to wait 15 minutes after blocking all new connections
    # this method can be used if you want to send out notifications to users that are still connected to save, log-off, etc.
time.sleep(900) 

print("...done wating 15 minutes.")

################################################################################################################################

#                                        ACTUAL DATABASE MAINTENANCE ACTIVITY BEGINS HERE:


################################################################################################################################

#                                                       DISCONNECT USERS:

print("Booting all users...")

# method to disconnect all SDE users
arcpy.DisconnectUser(db, 'ALL')

print("...all users Booted!\n ")

print("Printing list of all users to confirm all are disconnected...\n ")

# optional method to list all db users again after the DisconnectUser method (to make sure all users were indeed disconnected)
userList1 = arcpy.ListUsers(db)

#prints the above "userList1" variable to the system console
print(userList1)

################################################################################################################################

#                            METHOD TO CALL THE BATCH SCRIPT TO STOP THE SERVICE FOR ARCGIS SERVER:

#print("\nStopping the 'ArcGIS Server' service...")

#p = Popen("batchfile.bat", cwd=r"c:\directory\containing\batchfile")
#stdout, stderr = p.communicate()

#print("...'ArcGIS Server' service stopped!\n ")

################################################################################################################################

#                                                   LOG CURRENT DB VERSIONS:

print("Getting list of database versions...")

# gets a tuple of all current DB versions and assigns the tuple to the "versionList" variable
versionList = arcpy.ListVersions(db)

print("...done getting list of versions!\n ")

print("Writing list of versions to .txt file...")

# creates a file object for file I/O, with the name: "VersionList_beforeEditSession.txt" within the 
#  current maintenance period folder.  File is opened in write ('w') mode
file = open(os.path.join(currentFolderPath, "VersionList_beforeEditSession.txt"), 'w')

# loop to iterate over each item in the 'VersionList" tuple
for i in versionList:
     # take each item in the tuple, cast it to a String, then write it to the .txt file defined created in the previous step
	file.write(''.join(str(s) for s in i) + '\n')

    # method to close the file which saves the file and also prevents the file object from persisting in system memory
file.close()

print("...done writing list of versions to .txt file!\n ")

#################################################################################################################################

#                                                   RECONCILE & POST VERSIONS:

print("Reconciling, Posting, && Deleting versions....")

# method to Reconcile && Post && Delete all child versions up to DEFAULT
arcpy.ReconcileVersions_management(db, "ALL_VERSIONS", "dbo.DEFAULT", versionList, "LOCK_ACQUIRED", 
                                   "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_TARGET_VERSION","POST", 
                                   "DELETE_VERSION", reconcileFileName)

# NOTE: this method will also DELETE all child versions

print("...ALL VERSIONS RECONCILED, POSTED & ALL CHILD VERSIONS DELETED!!\n ")

################################################################################################################################

#                                                         DB COMPRESS:

print("Compressing database....")

# Run the compress tool. 
arcpy.Compress_management(db)

print("....Database compress complete!\n ")

print("Rebuilding indexes....")

# Rebuild indexes and analyze the states and states_lineages system tables
arcpy.RebuildIndexes_management(db, "SYSTEM", "", "ALL")

print("....done rebuilding indexes!\n ")

################################################################################################################################

#                                                   ANALYZE  SYSTEM  TABLES:

print("Analyzing database....")

# method to analyze the states and states_lineages system tables
arcpy.AnalyzeDatasets_management(db, "SYSTEM", "", "ANALYZE_BASE", "ANALYZE_DELTA", "ANALYZE_ARCHIVE")

print("....analysis complete!\n ")

################################################################################################################################                       

#                                          ALLOW NEW CONNECTIONS TO THE DATABASE:

print("Re-allowing database connections....")

arcpy.AcceptConnections(db, True)

print("...database now accepting new connections!\n ")


################################################################################################################################

#                          METHOD TO CALL THE BATCH SCRIPT TO RESTART THE SERVICE FOR ARCGIS SERVER:

#print("\nRestarting the 'ArcGIS Server' service...")

#p = Popen("batchfile.bat", cwd=r"c:\directory\containing\batchfile")
#stdout, stderr = p.communicate()

#print("...'ArcGIS Server' service Started!\n ")



################################################################################################################################ 

#                                               RE-CREATE ALL USER VERSIONS:

print("Re-creating database versions....")

# Set local variables
parentVersion    = "dbo.QC"
versionName      = "QC"
accessPermission = "PROTECTED"

print("....\n ")

# creates a QC version w/ parent version= 'DEFAULT'  # all user versions have parent version= 'QC'
arcpy.CreateVersion_management(db, "dbo.DEFAULT", versionName, "PUBLIC")

# loop to iterate over each user in the userList tuple & recreate that version
for version in versionList:  # "versionList" variable defined in line *161* above
	
	 # if statement to find all named (user) versions
    if(version != "dbo.DEFAULT" and version != "DBO.QC"):
        if("DBO." in version or "dbo." in version):
            versionName = version[4:]
            arcpy.CreateVersion_management(db, parentVersion, versionName, accessPermission)
        else: 
            versionName = version
            arcpy.CreateVersion_management(db, parentVersion, versionName, accessPermission)
    else: 
        continue # this will skip over the "dbo.DEFAULT" & "DBO.QC" items in the versionList tuple

print("ALL VERSIONS RECREATED!!!\n ")

################################################################################################################################

#                                         LOG DB VERSIONS AFTER DB MAINTENANCE:

print("Getting list of new versions...")

# list all current versions, assigne to new "versionList2" varaiable
versionList2 = arcpy.ListVersions(db)

print("...done getting list of versions!\n ")


print("Writing list of versions to .txt file...")

# creates a file object for file I/O, with the name: "VersionList_AfterEditSession.txt" within the 
#  current maintenance period folder.  File is opened in write ('w') mode
file = open(os.path.join(currentFolderPath, "VersionList_AfterEditSession.txt"), 'w')

# loop to iterate over each item in the 'VersionList2" tuple
for i in versionList2:
     # take each item in the tuple, cast it to a String, then write it to the .txt file defined created in the previous step
    file.write(''.join(str(s) for s in i) + '\n')

# method to close the file which saves the file and also prevents the file object from persisting in system memory
file.close()

print("...new versions logged in .txt file!\n ")

print("\nMAINTENANCE COMPLETE!")

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
