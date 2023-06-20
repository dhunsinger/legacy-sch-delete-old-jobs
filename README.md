# legacy-sch-delete-old-jobs


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
