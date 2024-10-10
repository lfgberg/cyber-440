import xml.etree.ElementTree as ET
import xmltodict
import json
import os
from datetime import datetime

# Parse the XML file
tree = ET.parse('events.xml')  # Replace 'events.xml' with your actual file path
root = tree.getroot()

# Helper function to remove namespaces from dictionary keys
def remove_namespace(d):
    if isinstance(d, dict):
        return {k.split(':')[-1]: remove_namespace(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [remove_namespace(i) for i in d]
    else:
        return d

# Function to convert timestamp to desired format
def format_timestamp(ts):
    if ts:
        # Remove the 'Z' at the end and handle the fractional seconds
        ts = ts.replace("Z", "")  # Remove the 'Z' character
        # Split the timestamp into the main part and the fractional part
        if '.' in ts:
            main_part, fractional_part = ts.split('.')
            # Limit the fractional part to 6 digits
            fractional_part = fractional_part[:6]
            ts = f"{main_part}.{fractional_part}"
        else:
            ts = ts
            
        # Parse the original timestamp and format it
        original_time = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        return original_time.strftime("%Y-%m-%d %H:%M:%S")
    return None

# List to hold all events
all_events = []

# Loop through each event and convert to a dictionary
for event in root:
    # Convert XML event to dictionary
    event_dict = xmltodict.parse(ET.tostring(event))

    # Remove namespace prefixes from the dictionary
    event_dict = remove_namespace(event_dict)

    # Check if 'Event' key exists (after removing namespaces)
    if 'Event' in event_dict:
        # Extract necessary fields for a flat structure
        event_data = {}

        # Extract System fields
        system_fields = event_dict['Event']['System']
        event_data['event_id'] = system_fields.get('EventID')
        event_data['level'] = system_fields.get('Level')
        event_data['task'] = system_fields.get('Task')
        
        # Format the timestamp
        original_timestamp = system_fields.get('TimeCreated', {}).get('@SystemTime')
        event_data['@timestamp'] = format_timestamp(original_timestamp)
        
        event_data['computer'] = system_fields.get('Computer')
        event_data['channel'] = system_fields.get('Channel')

        # Extract EventData fields
        if 'EventData' in event_dict['Event']:
            for data in event_dict['Event']['EventData'].get('Data', []):
                field_name = data.get('@Name')
                field_value = data.get('#text')
                if field_name and field_value is not None:
                    event_data[field_name] = field_value  # Add only if field name is valid

        # Add the event to the list
        all_events.append(event_data)
    else:
        print(f"Skipped an event without 'Event' tag: {event_dict}")

# Function to manage writing to multiple files based on size limit
def write_ndjson_splitted(events, max_file_size_mb=100):
    file_index = 1
    file_size = 0
    max_file_size = max_file_size_mb * 1024 * 1024  # Convert MB to bytes
    current_file = open(f'events_{file_index}.ndjson', 'w')

    for event in events:
        # Convert event to JSON string
        event_json = json.dumps(event) + '\n'
        event_size = len(event_json.encode('utf-8'))  # Get the byte size of the event

        # Check if adding the event exceeds the file size limit
        if file_size + event_size > max_file_size:
            # Close current file and open a new one
            current_file.close()
            file_index += 1
            current_file = open(f'events_{file_index}.ndjson', 'w')
            file_size = 0  # Reset file size counter for the new file

        # Write event to the current file
        current_file.write(event_json)
        file_size += event_size

    # Close the last file
    current_file.close()

# Write events to NDJSON files, splitting at 100MB
write_ndjson_splitted(all_events, max_file_size_mb=100)

print("Events have been successfully converted to flat NDJSON files!")
