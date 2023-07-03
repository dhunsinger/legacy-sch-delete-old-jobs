#!/usr/bin/env python

'''
This script exports and deletes Jobs from StreamSets Control Hub 3.x
older than a configurable number of days before now. Jobs must have
INACTIVE status to be processed, and must have been run at least once.

Note that Control Hub will automatically delete Jobs that have never been run after one year.

Prerequisites:
 - Python 3.6+; Python 3.9+ preferred

 - StreamSets SDK for Python v3.12.1
   See: https://docs.streamsets.com/sdk/latest/installation.html

 - Username and password for a user with Organization Administrator role

 - To avoid including secrets in the script, export these two environment variables
   prior to running the script:
        export USER=<your Org Admin USER ID in the form user@org>
        export PASS=<your PASSWORD>

 - Set the variable DRY_RUN = True to export the Jobs identified for deletion
      without actually deleting any Jobs

 - Set the variable DRY_RUN = False to export the Jobs identified for deletion
      and to actually delete the Jobs

 - Set the variable EXPORT_BASE_DIR to the directory where you want to export Jobs

 - Set the variable NUM_DAYS to the number of days to consider a Job old

 - Set the variable LABEL to define job Data Collector Label used to mark old jobs
   for deletion. If a job is old enough, but not labeled, it will not be deleted.
   Setting a job's data collector label without matching SDC labels
   will also ensure the jobs do not execute before deletion.

Usage Instructions:

Run the script with the variable DRY_RUN = True to print a list of Jobs that are marked for deletion.
A DRY_RUN will also export each Job marked for deletion into a timestamped child dir within the EXPORT_BASE_DIR.

After running a DRY_RUN, inspect the list of Jobs identified for deletion. Then
try manually deleting one or two of those Jobs from Control HUb, and confirm that 
you can importing the corresponding exported Jobs.

If all goes well, then run the script again with DRY_RUN = False to actually delete the Jobs

'''

import os
from time import time
import sys
import datetime
from streamsets.sdk import ControlHub

## User Variables ##################

# DRY_RUN
# Set DRY_RUN = True to export the Jobs identified for deletion
# without actually deleting any Jobs 
# Set DRY_RUN = False to export the Jobs identified for deletion
# and to actually delete the Jobs
DRY_RUN = True

# Get user_id from environment
USER_ID = os.getenv('USER')

# Get password from the environment
PASS = os.getenv('PASS')

# Control Hub URL, e.g. https://cloud.streamsets.com
SCH_URL = 'https://cloud.streamsets.com'

# Jobs Export dir
EXPORT_BASE_DIR = '<YOUR EXPORT DIR>'

# Number of days before today to search for jobs to delete
NUM_DAYS = 365

# SDC Label to identify old jobs to delete
LABEL = 'delete'

## End User Variables ##############

# Connect to Control Hub
sch = ControlHub(
    SCH_URL,
    USER_ID,
    PASS)

# print header method
def print_header(header):
    divider = 60 * '-'
    print('\n' + divider)
    print(header)
    print(divider)

# mkdir method
def mkdir(dir_to_create):
    path =   os.path.join(EXPORT_BASE_DIR, dir_to_create)
    if not os.path.exists(path):
        os.mkdir(path)

# Create the export directory if it does not exist
if not os.path.exists(EXPORT_BASE_DIR):
    try:
        os.mkdir(EXPORT_BASE_DIR)
    except Exception as err:
         print('Error creating export directory: ' + str(err))
         sys.exit(-1)

# export_resource method
def export_resource(export_dir, resource_name, data):

    # replace '/' with '_' in resource name
    resource_name = resource_name.replace('/', '_' )

    # Export a zip file for the resource
    with open(export_dir + '/' + resource_name + '.zip', 'wb') as file:
        file.write(data)

#calculate timestamp for filtering old jobs - now minus NUM_DAYS in ms
now = round(time() * 1000)
num_to_ms = NUM_DAYS * 24 * 60 * 60 * 1000
as_of = now - num_to_ms
dt = datetime.datetime.fromtimestamp(as_of / 1000.0)

if DRY_RUN:
    print_header('Script is running in DRY_RUN mode.\nJobs marked for deletion will be exported only and NOT deleted')
else:
    print_header('Script is NOT running in DRY_RUN mode.\nJobs marked for deletion will be exported AND deleted')

# Get jobs for deletion
print(f'\nRetrieving inactive jobs finished before {dt}\ncontaining label \"{LABEL}\"')
jobs = [job for job in sch.jobs if job.history and job.history[0].finishTime < as_of and job.status == 'INACTIVE']
filtered_jobs = []
for job in jobs:
    if LABEL in job.data_collector_labels:
        filtered_jobs.append(job)
# Exit if no old Jobs found
if filtered_jobs is None or len(filtered_jobs) == 0:
    print('Script halted. No old Jobs found\n')
    sys.exit(0)

# Print list of Jobs marked for deletion
print(f'\nJobs targeted for deletion:')
print(60 * '-')
for job in filtered_jobs:
    last_run_finish_time = datetime.datetime.fromtimestamp(job.history[0].finishTime/1000.0)
    print('Job: \'' + job.job_name + '\'     Last Run: ' + last_run_finish_time.strftime("%Y-%m-%d %H:%M:%S") )
print(60 * '-')
print(f'Total Number of Jobs targeted for deletion: {len(filtered_jobs)}')

# Create export dir based on current timestamp
export_dir = EXPORT_BASE_DIR + '/' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") 

# Export Jobs marked for deletion
print_header('Exporting Jobs to ' + export_dir)
mkdir(export_dir)
for job in filtered_jobs:
    data = sch.export_jobs([job])
    print('Exporting Job \'' + job.job_name + '\'')
    export_resource(export_dir, job.job_name, data)

# If not a DRY_RUN, delete the selected Jobs
if not DRY_RUN:
    do_it = input('\nDo you want to delete the selected Jobs? (Y/N)?')
    #Delete Jobs
    if do_it == 'Y':
        print_header('Deleting selected Jobs...')
        for job in filtered_jobs:
            try:
                print('Deleting Job \'' + job.job_name + '\'')
                sch.delete_job(job)
            except Exception as e:
                print(f"An exception occurred while trying to delete the Job {job.job_name}") 
                print(str(e)) 
                print('The script will exit without trying to delete any more Jobs')
                sys.exit(-1)
    else:
        print('\nScript aborted; no Jobs deleted')

print_header('Finished')
