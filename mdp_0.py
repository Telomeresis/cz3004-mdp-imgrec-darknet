from img_comm_get import *
import pandas as pd
import time
from partitioning_helper_0 import *
import os.path
from os import path

# Declare rec object to do communications
rec = RecAPI()
rec.init_pc_comm()


i = 1 # Counter to track iterations of loop cycle
while (True): # while loop

    # # # # # # # # # # # # # #
    # COMMENCE JSON PRE-CHECK #
    # # # # # # # # # # # # # #

    # Retrieve True/False value for existence of JSON file
    json_exists = path.exists("mdpfiles/predicted_output/result.json")
    if (json_exists == True): # If JSON file exists
        #print('JSON file exists.')

        # Retrieve size of JSON file that already exists
        size = os.stat('mdpfiles/predicted_output/result.json').st_size

        # Print size of JSON file
        #print('JSON File Size: {}'.format(size))

        if (size != 0): # If JSON file has some shit inside
            print('')
            print('JSON FILE SIZE:'.format(size))
            print('▶ {}'.format(size))
            # # # # # # # # # # # # # # #
            # COMMENCE MDP PART 3 CODE  #
            # # # # # # # # # # # # # # #

            # Load and parse json data produced by Darknet
            # [NOTE] There is a potential problem here when I receive corrupted images, although grace's laptop has no issues.
            all_images = load_json('mdpfiles/predicted_output/result.json')

            # Create initial df using json data
            df = declare_df(all_images)

            # Determine distance offsets and update df with new column
            df = calculate_distance_offset(df)

            # Get paths to each image in input directory
            image_list = get_filelist('mdpfiles/samples') # CHANGE BACK TO // IF THERE ARE ANY PROBLEMOSSS

            # Create image_df using image_list and get initial dimensions for each image in directory
            image_df = declare_image_df(image_list)

            # Create concatenated df using df and image_df
            final_df = pd.concat([df, image_df], axis=1, sort=False)

            # Drop NaN rows
            final_df = final_df.dropna()

            # Calculate Left and Right Boundaries
            final_df = calculate_partitions(final_df)

            # Determine offset using L/R Boundaries
            final_df = determine_offsets(final_df)

            # Store received robot x,y,o values from buffer into final_df
            final_df = retrieve_text_metadata(final_df)

            # Calculate actual x and y axis values
            final_df = calculate_actual_coordinates(final_df)

            # Map actual image ID
            final_df = map_actual_image_id(final_df)

            # Create df using only unique first instances
            unique_df = declare_unique_df(final_df)

            # Generate output string
            output_string = declare_output_string(unique_df)
            print('OUTPUT STRING GENERATED:')
            print('▶▶ {} '.format(output_string))
            print('')
            '''
            END MDP PART 3 CODE
            '''

            # COMMENCE MESSAGE SENDING TO ANDROID PART

            '''
            # CODE TO SEND MESSAGE TO ANDROID
            send_msg = output_string # uses output string from previous functions
            print("write_to_Android(): ", send_msg)
            rec.write_to_Android(send_msg.encode())
            print('Sent to Android')

            # CHECK IF 5 UNIQUE PICTURES HAVE BEEN FOUND TO END CONNECTION PREMATURELY
            if (len(unique_df.index) >= 5):
                print("closing sockets")
                # Close sockets
                rec.close_pc_socket()
                print('Image recognition completed - 5 unique classes detected.')
                # call function to stitch image
                break
            '''

            # END MESSAGE SENDING TO ANDROID PART

print('El finito')
