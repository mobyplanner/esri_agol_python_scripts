## Workforce Export Assignments
This script reads the assignment feature layer of the Workforce project and save all informations into Excel file.

The script specific arguments are as follows:
- -u \<userName\> -> AGOL username
- -p \<password\> -> AGOL password
- -pn \<projectName\> -> Workforce project name
- -h -> show this help

#### Example usage:
```python
python workforceAssignmentsExport.py -u 'username' -p 'password' -pn 'projectName'
```

#### Requirements:
- Esri Workforce project w/ assignment set

#### What it does
 1. First the script uses the provided credentials to authenticate with AGOL
 2. Then is determined workforce Project ID based on Project Name
 3. Export all tasks into Excel file