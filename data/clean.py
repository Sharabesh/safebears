import pandas as pd

calls = pd.read_csv("crime_raw.csv")

# Convert CVDOW to weekday
weekday_mapping = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
calls['Day'] = calls['CVDOW'].map(weekday_mapping)

# Assign crime severity
severity_mapping = {"LARCENY": 1, "BURGLARY - VEHICLE": 2, "DISORDERLY CONDUCT": 3, "ASSAULT": 4, "VANDALISM": 5, "MOTOR VEHICLE THEFT": 6, "FRAUD": 7, "BURGLARY - RESIDENTIAL": 8, "ROBBERY": 9, "DRUG VIOLATION": 10, "BURGLARY - COMMERCIAL": 11, "FAMILY OFFENSE": 12, "LARCENY - FROM VEHICLE": 13, "WEAPONS OFFENSE": 14, "LIQUOR LAW VIOLATION": 15, "MISSING PERSON": 16, "SEX CRIME": 17, "ARSON": 18, "RECOVERED VEHICLE": 19, "KIDNAPPING": 20, "NOISE VIOLATION": 21, "ALL OTHER OFFENSES": 22, "HOMICIDE": 23}
calls['Severity'] = calls["CVLEGEND"].map(severity_mapping)

# Parse hour of crime from EVENTTM
calls['Hour'] = calls['EVENTTM'].str.slice(0,2).astype(int)

# Parse latitude and longitude from Block_Location
calls = calls.join(
        calls['Block_Location']
        # Get coords from string
        .str.split('\n').str[2]
        # Remove parens from coords
        .str[1:-1]
        # Split latitude and longitude
        .str.split(', ', expand=True)
        .rename(columns={0: 'Latitude', 1: 'Longitude'})
    )

# Drop unnecessary columns and rename CVLEGEND to Crime
calls = calls.loc[:, ['CVLEGEND', 'Severity', 'Latitude', 'Longitude', 'Day', 'Hour']].rename(index=str, columns={'CVLEGEND':'Crime'})

# Drop rows with missing/null values
calls.dropna(inplace=True)

calls.to_csv('crime_clean.csv')