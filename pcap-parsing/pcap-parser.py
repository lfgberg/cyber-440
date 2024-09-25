import json
import time

def main():
    # Start the clock
    start = time.time()

    # Load the JSON file
    data = readJson('network-map.json')

    # Parse the data
    results = parseData(data)

    # Save the results
    saveResults(results, 'results.json')

    # Stop the clock
    end = time.time()

    print("The time of execution of above program is :",
      (end-start) * 10**3, "ms")
    
    exit()

def saveResults(results, fileName):
    with open(fileName, 'w') as outfile:
        json.dump(results, outfile, indent=4)

def parseData(data):
    results = {}

    for entry in data:
        # 1. check to see if we've seen the src host before
        if entry['Source'] not in results:
            results[entry['Source']] = {'UDP': [], 'TCP': []}

        # 2. check to see if the port is open on the src host & add if so
        if ((entry['SrcPort'] < entry['DestPort']) & (entry['SrcPort'] <= 49151)):

            # 3. Check TCP or UDP
            if (entry['Protocol'] == "TCP"):
                # 4. Check if we've seen before or not
                if entry['SrcPort'] not in results[entry['Source']]['TCP']:
                    # 5. Append
                    results[entry['Source']]['TCP'].append(entry['SrcPort'])
            else:
                # 4. Check if we've seen before or not
                if entry['SrcPort'] not in results[entry['Source']]['UDP']:
                    # 5. Append
                    results[entry['Source']]['UDP'].append(entry['SrcPort'])
    
    return results

def readJson(filePath):
    # Load the JSON file
    with open(filePath, 'r') as file:
        data = json.load(file)
    
    # Return the data
    return data

if __name__=="__main__":
    main()