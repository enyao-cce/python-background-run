import requests
import time, math
from class1 import InitialPass

# Define the API endpoint URLs

api_parameter = 'http://127.0.0.1:80/paraLatest'
api_update_toStop = 'http://127.0.0.1:80/updateToStop'
api_update_phyStatus = 'http://127.0.0.1:80/updatePhyStatus'
api_readChar = 'http://127.0.0.1:80/BCLatestRowall'
api_updateExpStatus = 'http://127.0.0.1:80/updateExpStatus'
api_switch_currentx = 'http://127.0.0.1:80/injectc'


new_instance = InitialPass()

# Main script loop
while True:
    # Get parameter stuff latest row
    paraStuff_response = requests.get(api_parameter)
    updatePhyStatus = requests.post(api_update_phyStatus, json={'phy_status': 1})

    data = paraStuff_response.json()
  

    if data:
        try:
            if data['phy_start'] == 1:
                 # Execute the class function
                 new_instance.startingUP()
                 
                 # add code here
                 # if phy_status in last row is not 0
                 requests.post(api_switch_currentx, json={'c': 0 }); #in case there is a current before start

                 new_instance.starting_BC_check()
                 phy_status = updatePhyStatus.json()
                 phy_status_value = int(phy_status['message'])  # Convert 'message' to an integer
    
                 # Get the latest row of BC_IOT
                 BC_response = requests.get(api_readChar)
                 capacity =  math.floor(BC_response.json()['capacity'])
                 SOC_max = BC_response.json()['SOC_max']
                 expStatus = BC_response.json()['expStatus']
               
                 # Check if capacity is less than SOC_max
                 while capacity < SOC_max and expStatus !=2 and expStatus !=5 and data['phy_start'] == 1:

                    new_instance.error_check()
                    new_instance.running()
                    new_instance.startingUP()
                    

                    # Get the latest row of BC_IOT
                    check_resp = requests.get(api_readChar)
                    capacity =  math.floor(check_resp.json()['capacity'])
                    SOC_max = check_resp.json()['SOC_max']
                    expStatus = check_resp.json()['expStatus']
                    print("capacity is  " + str(capacity) + ", while SOC_max is " + str(SOC_max))

                    

                    # Sleep for 30 seconds before checking capacity again
                    time.sleep(30)

                 time.sleep(10)
                 #Current will go to 0 when SOC_max is reached
                 responding = requests.get("http://127.0.0.1:80/charBMS"); #switch off the Mos_charge
                

                 if capacity >= SOC_max and data['phy_start'] == 1:
                    update_response = requests.post(api_update_toStop, json={'phy_start': 0})
                    update_status = requests.post(api_updateExpStatus, json={'newExpStatus': 1})
                    print("Experiment completed")
                 elif data['phy_start'] == 1:
                    # Capacity is equal to or greater than SOC_max, update phy_start to 0
                    update_response = requests.post(api_update_toStop, json={'phy_start': 0})

                 if update_response.status_code == 200:
                    print("Successfully updated 'phy_start' value to 0.")
                 else:
                    print("Failed to update 'phy_start' value to 0.")

         
        except KeyError:
            print("phy_start key not found, dataTable empty")
            pass
    
    print("phy_start is not 1")
   
          
    # Sleep for 30 seconds before checking phy_start again
    time.sleep(30)
