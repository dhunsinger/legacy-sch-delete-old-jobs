# legacy-sch-delete-old-jobs

This script exports and deletes Jobs from StreamSets Control Hub 3.x
older than a configurable number of days before now. Jobs must have
INACTIVE status to be processed, and must have been run at least once.

Note that Control Hub will automatically delete Jobs that have never been run after one year.

## Prerequisites:
 - Python 3.6+; Python 3.9+ preferred

 - StreamSets SDK for Python v3.12.1
   See: https://docs.streamsets.com/sdk/latest/installation.html

 - Username and password for a user with Organization Administrator role

 - To avoid including secrets in the script, export these two environment variables
   prior to running the script:
   
<code>export USER=[your Org Admin USER ID in the form user@org]</code><BR>
<code>export PASS=[your PASSWORD]</code>

 - Set the variable DRY_RUN = True to export the Jobs identified for deletion
      without actually deleting any Jobs

 - Set the variable DRY_RUN = False to export the Jobs identified for deletion
      and to actually delete the Jobs

 - Set the variable EXPORT_BASE_DIR to the directory where you want to export Jobs

 - Set the variable NUM_DAYS to the number of days to consider a Job old

## Usage Instructions:

Run the script with the variable <code>DRY_RUN = True</code> to print a list of Jobs that are marked for deletion.
A DRY_RUN will also export each Job marked for deletion into a timestamped child dir within the EXPORT_BASE_DIR.

After running a DRY_RUN, inspect the list of Jobs identified for deletion. Then
try manually deleting one or two of those Jobs from Control Hub, and confirm that 
you can importing the corresponding exported Jobs.

If all goes well, then run the script again with DRY_RUN = False to actually delete the Jobs.

Here is example console output from runs of the script in both modes:

### Example run with <code>DRY_RUN = True</code>

% python3 delete-old-jobs.py

Script is running in DRY_RUN mode.
Jobs marked for deletion will be exported only and NOT deleted

Retrieving inactive jobs finished before 2022-06-20 19:33:26.481000

Jobs targeted for deletion:

Job: 'Job 1'     Last Run: 2022-06-20 19:22:50<BR/>
Job: 'Job 2'     Last Run: 2022-06-20 19:22:50<BR/>
Job: 'Job 3'     Last Run: 2022-06-20 19:22:50<BR/>

Total Number of Jobs targeted for deletion: 3


Exporting Jobs to /Users/mark/data/clean-up-jobs/2023-06-20-19-33-27

Exporting Job 'Job 1'<BR/>
Exporting Job 'Job 2'<BR/>
Exporting Job 'Job 3'<BR/>


Finished


### Example run with <code>DRY_RUN = False</code>. Note the prompt to confirm Job deletion:


````
% python3 delete-old-jobs.py

--------------------------------------------------------
Script is NOT running in DRY_RUN mode.
Jobs marked for deletion will be exported AND deleted
--------------------------------------------------------

Retrieving inactive jobs finished before 2023-06-20 19:43:44.083000

--------------------------------------------------------
Jobs targeted for deletion:
--------------------------------------------------------
Job: 'Job 1'     Last Run: 2023-06-20 19:22:50<BR/>
Job: 'Job 2'     Last Run: 2023-06-20 19:22:50<BR/>
Job: 'Job 3'     Last Run: 2023-06-20 19:22:50<BR/>
--------------------------------------------------------
Total Number of Jobs targeted for deletion: 3

--------------------------------------------------------
Exporting Jobs to /Users/mark/data/clean-up-jobs/2023-06-20-19-43-45
--------------------------------------------------------
Exporting Job 'Job 1'<BR/>
Exporting Job 'Job 2'<BR/>
Exporting Job 'Job 3'<BR/>

Do you want to delete the selected Jobs? (Y/N)?Y

--------------------------------------------------------
Deleting selected Jobs...
--------------------------------------------------------
Deleting Job 'Job 1'<BR/>
Deleting Job 'Job 2'<BR/>
Deleting Job 'Job 3'<BR/>

--------------------------------------------------------
Finished
--------------------------------------------------------

````