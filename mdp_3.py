from partitioning_helper import *
import pandas
import time
from img_comm_get import *


pandas.set_option('display.max_rows', None)


def run_partioning(rec):

    # need code to initialize rec, or pass in rec from mdp_1.py
    #rec = RecAPI()

    #rec.init_pc_comm() # don't need to initialize as we already initialized in script 1

    print('PARTIONING IN PROCESS')
    # Load and parse json data produced by Darknet
    all_images = load_json('mdpfiles/predicted_output/result.json')
    # Create initial df using json data
    df = declare_df(all_images)
    # Determine distance offsets and update df with new column
    df = calculate_distance_offset(df)
    # Get paths to each image in input directory
    image_list = get_filelist('mdpfiles\\samples')
    # Create image_df using image_list and get initial dimensions for each image in directory
    image_df = declare_image_df(image_list)
    # Create concatenated df using df and image_df
    final_df = pd.concat([df, image_df], axis=1, sort=False)
    # Calculate Left and Right Boundaries
    final_df = calculate_partitions(final_df)
    # Determine offset using L/R Boundaries
    final_df = determine_offsets(final_df)
    # Store received robot x,y,o values from buffer into final_df
    final_df = retrieve_buffer_values(final_df)
    # Calculate actual x and y axis values
    final_df = calculate_actual_coordinates(final_df)
    # Map actual image ID
    final_df = map_actual_image_id(final_df)
    # Create df using only unique first instances
    unique_df = declare_unique_df(final_df)
    print('PARTIONING IS COMPLETED PROCESS')
    return unique_df
