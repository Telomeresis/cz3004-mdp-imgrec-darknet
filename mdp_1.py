from img_comm_get import *
import pandas as pd
import time
from mdp_3 import *
from partitioning_helper import *
import os.path
from os import path

def process_dd(decoded_data, x_list, y_list, orientation_list):
    print("START OF PROCESS_DD")
    # get list of raw values, temporary placeholder
    dd_list = decoded_data.split(',')
    # append raw values to respective global lists
    x_list.append(dd_list[0])
    y_list.append(dd_list[1])
    orientation_list.append(dd_list[2])
    # re/initialize df to wipe the slate clean
    df = pd.DataFrame(columns = ['x', 'y', 'orientation'])
    # append lists to respective dataframes
    df['x'] = x_list
    df['y'] = y_list
    df['orientation'] = orientation_list
    # write dataframe to text file
    print("Write to decoded_raw.txt")
    df.to_csv('mdpfiles/predicted_output/decoded_raw.csv', index=False)
    print(dd_list)


# Declare rec object
rec = RecAPI()
rec.init_pc_comm()

# initialize list to temporarily store data
x_list = []
y_list = []
orientation_list = []
# needed for output file naming convention

i = 1
while (True):
    data = rec.read_coor()
    # [mdp_1 code] Retrieve Coordinates,
    if (data != None):
        decoded_data = data.decode()
        #print(decoded_data)
        if (decoded_data != ''):
            # Process Decoded Data
            process_dd(decoded_data, x_list, y_list, orientation_list)
            print('process complete')
            print(str(i))
            i+=1
    print('SPACE BETWEEN STARS')
    print('')

    # [mdp_3 code]
    if (path.exists("C:/Users/SAMARITAN/git/darknet/mdpfiles/predicted_output/result.json")):
        print('Check if json file is updated')
        size = os.stat('C:/Users/SAMARITAN/git/darknet/mdpfiles/predicted_output/result.json').st_size
        print(str(size))

        size = os.stat('C:/Users/SAMARITAN/git/darknet/mdpfiles/predicted_output/result.json').st_size
        if (size != 0):
            print('JSON file has been updated')
            unique_df = run_partioning(rec)
            output_string = declare_output_string(unique_df)
            # CODE TO SEND MESSAGE TO ANDROID
            send_msg = output_string # uses output string from previous functions
            print("write_to_Android(): ", send_msg)
            rec.write_to_Android(send_msg.encode())
            print('Sent to Android')

            # check if unique_df rows >= 5
            if (len(unique_df.index) >= 5):
                print("closing sockets")
                # Close sockets
                rec.close_pc_socket()
                print('Image recognition completed - 5 unique classes detected.')
                # call function to stitch image
                break
print('El finito')
