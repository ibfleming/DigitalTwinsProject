"""
Test one of the saved sessions that is stored in the database.

This will allow us to look at past data from the database
"""

import os
import pyarrow as pa
import pyarrow.parquet as parq
import pandas as pd

# Storage head for replays
storageHead = os.getcwd()
print(storageHead)
storageMiddle = "/PastSessionStorage/"
storageEnd = ".parquet"
fileFound = False

# Define the schema
schema = pa.schema([
    ("Time", pa.timestamp('ms')),
    ("Data", pa.string())
])

# Read the parquet data file
def read_parquet_data(table):
    tempTable = parq.read_table(table).to_pandas()
    print(tempTable)

    print(tempTable.iloc[0])

# Main Function
def main():
    #Load in the global storage variables
    global storageHead
    global storageMiddle
    global storageEnd
    global fileFound

    # Get the replay that you would like to view here
    while(fileFound == False):
        val = input("Enter the past file name: ")
        try:
            storageHead = storageHead + storageMiddle + val.strip() + storageEnd
            print(storageHead + "\n")
            print(type(storageHead))
        
            read_parquet_data(storageHead)
            fileFound = True
        except:
            print("ERROR: The inputted file name was not found... \n Please try again...")

        
        
if __name__ == "__main__":
    main()