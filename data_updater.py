import json
import os
import sys
from deepdiff import DeepDiff
from datetime import datetime
from prompter import print_success, print_error, print_warning

def validate_and_create_path(path=None):
    # Use the current working directory as a default for the path
    path = path or os.path.join(os.environ.get('PWD', ''), 'data')
    
    try:
        # Ensure that the directory exists, create it if it doesn't
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        # Exit with a failure code if there is an error creating the path
        print_error(f"Error creating path: {e}")
        sys.exit(1)
    
    return path

def parse_date(date_str):
    try:
        # Split and strip the date part (ignore the day of the week)
        date_part = date_str.split(" ")[0].strip().replace(",", "")
        # Convert it to a timestamp
        return datetime.strptime(date_part, "%Y-%m-%d").timestamp()
    except ValueError:
        # Return a default value if there's an issue with the date format
        return 0

def sort_by_date(data, data_key=None):
    sort_key = "date"
    if data_key:
        sort_key += f"_{data_key}"
    return sorted(data, key=lambda x: parse_date(x[sort_key]), reverse=True)

def update_data(table_data):
    # Validate path and set the json file path
    data_path = validate_and_create_path()
    json_path = os.path.join(data_path, 'data.json')
    
    data = {}

    # Check if the JSON file exists
    if os.path.exists(json_path):
        try:
            # Read existing data from the JSON file
            with open(json_path, 'r') as json_file:
                data = json.load(json_file)
            
            # Ensure both `data` and `table_data` are dictionaries
            for keys in table_data:
                if isinstance(data, dict) and isinstance(table_data, dict):
                    if keys in data:
                        # Check if `data[keys]` and `table_data[keys]` are dictionaries
                        if isinstance(data[keys], dict) and isinstance(table_data[keys], dict):
                            for key in table_data[keys]:
                                # Ensure both are dictionaries before accessing their keys
                                if key in data[keys] and data[keys][key] != table_data[keys][key]:
                                    data[keys][key] = table_data[keys][key]
                        else:
                            # If `keys` in data or table_data is not a dictionary, skip or handle as needed
                            data[keys] = table_data[keys]
                    else:
                        # Add missing `keys` from `table_data` if not present in `data`
                        data[keys] = table_data[keys]
        except Exception as e:
            print(f"An error occurred while reading the JSON file: {e}")
    else:
        # If the file does not exist, initialize `data` with `table_data`
        data = table_data
    
    # Sort the data by date for each key
    sorted_data = {}
    for key in data:
        sort_cat = 'filed' if key != 'attendance' else None
        sorted_data[key] = sort_by_date(data[key], sort_cat)
    
    # Write the updated data back to the JSON file
    try:
        with open(json_path, 'w') as json_file:
            json.dump(sorted_data, json_file, indent=2)
        print_success("Data saved.")
    except Exception as e:
        print_error(f"Error writing to JSON file: {e}")
        sys.exit(1)