## Load Unassigned Tasks into Esri Workforce
This script reads an xlsx file containing the required fields to load tasks into an Esri Workforce project.

The script specific arguments are as follows:
- -u \<userName\> -> AGOL username
- -p \<password\> -> AGOL password
- -pn \<projectName\> -> Workforce project name
- -f \<xlsxFile\> -> XLSX File to upload
- -h -> show this help

#### Example usage:
```python
python workforceAssignmentsBulkLoad.py -u 'username' -p 'password' -pn 'projectName' -f '../sampleData/workforceBasketAssignments.xlsx'
```

#### Requirements:
- Esri Workforce project w/ assignment types set

#### What it does
 1. First the script uses the provided credentials to authenticate with AGOL
 2. Then is determined workforce Project ID based on Project Name
 3. Next asks deletion or not in case the feature layer in not empty
 4. Upload all rows of XLSX file into assignment feature layer of workforce project


