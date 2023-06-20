#!/usr/bin/env python

'''
This script exports and deletes Jobs from StreamSets Control Hub 3.x
older than a configurable number of days before now. Job must have
INACTIVE status to be processed.

Prerequisites:
 - Python 3.6+; Python 3.9+ preferred

 - StreamSets SDK for Python v3.12.1
   See: https://docs.streamsets.com/sdk/latest/installation.html

 - Username and password for a user with Organization Administrator role
 - To avoid including secrets in the script, export these two environment variables
   prior to running the script:
        export USER=<your Org Admin USER ID>
        export PASS=<your PASSWORD>

'''

import os
from time import time
import sys
import datetime
from streamsets.sdk import ControlHub

## User Variables ##################

# # Get user_id from environment
USER_ID = os.getenv('USER')

# Get password from the environment
PASS = os.getenv('PASS')

# Control Hub URL, e.g. https://cloud.streamsets.com
SCH_URL = 'https://cloud.streamsets.com'

# Export dir - change JOBS_DIR for multiple runs
EXPORT_BASE_DIR = '<your-export-dir>'

JOBS_DIR = 'jobs'

# Number of days before today to search for jobs to delete
NUM_DAYS = 365

## End User Variables ##############

# Connect to Control Hub
sch = ControlHub(
    SCH_URL,
    USER_ID,
    PASS)

# print header method
def print_header(header):
    divider = 60 * '-'
    print('\n\n' + divider)
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
print('\nExporting resources to ' + EXPORT_BASE_DIR)

# export_resource method
def export_resource(export_dir, resource_name, data):

    # replace '/' with '_' in resource name
    resource_name = resource_name.replace('/', '_' )

    # Export a zip file for the resource
    with open(EXPORT_BASE_DIR + '/' + export_dir + '/' + resource_name + '.zip', 'wb') as file:
        file.write(data)

#calculate timestamp for filtering old jobs - now minus NUM_DAYS in ms
now = round(time() * 1000)
num_to_ms = NUM_DAYS * 24 * 60 * 60 * 1000
as_of = now - num_to_ms
dt = datetime.datetime.fromtimestamp(as_of / 1000.0)

# Count total jobs
print_header('Retrieving all jobs from SCH')
before_jobs = 0
for job in sch.jobs:
    before_jobs+=1
print(f'Total jobs retrieved from SCH: {before_jobs}')

# Count jobs for deletion
print_header(f'Retrieving inactive jobs finished before {dt}')
after_jobs = 0
jobs = [job for job in sch.jobs if job.history and job.history[0].finishTime < as_of and job.status == 'INACTIVE']
for job in jobs:
    after_jobs += 1
print(f'Jobs targeted for export/deletion: {after_jobs}')

do_it = input('Do you want to proceed with export/deletion? (Y/N)?')
#Export Jobs
if do_it == 'Y':
    print_header('Exporting Jobs')
    mkdir(JOBS_DIR)
    for job in jobs:
        data = sch.export_jobs([job])
        print('Exporting Job \'' + job.job_name + '\'\n')
        export_resource(JOBS_DIR, job.job_name, data)
else:
    print_header('Script halted. Non jobs exported/deleted')
    sys.exit(0)

#Delete Jobs
if do_it == 'Y':
    for job in jobs:
        data = sch.delete_job(job)
        print('Deleting Job \'' + job.job_name + '\'\n')
print_header('Finished')






