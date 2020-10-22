import json
import pandas as pd
import numpy as np
import os
from PIL import Image


def load_json(json_directory):
    with open(json_directory) as json_file:
        data = json.load(json_file)
        all_images = []
        for each in data:
            pathname = each['filename']
            if (len(each['objects']) != 0):
                name = each['objects'][0]['name']
                x_axis = each['objects'][0]['relative_coordinates']['left_x']
                y_axis = each['objects'][0]['relative_coordinates']['top_y']
                box_width = each['objects'][0]['relative_coordinates']['width']
                box_height = each['objects'][0]['relative_coordinates']['height']
                box_area = box_width * box_height
                confidence = each['objects'][0]['confidence']
                image_info = [pathname, name, x_axis, y_axis, box_width, box_height, box_area, confidence]
                all_images.append(image_info)
        return all_images


def declare_df(all_images):
    columns = [
        'Path Name',
        'Description',
        'BBox X-axis',
        'BBox Y-axis',
        'BBox Width',
        'BBox Height',
        'BBox Area',
        'Confidence'
    ]
    df = pd.DataFrame(data = all_images, columns = columns)
    return df


def calculate_distance_offset(df): # need to put it in another script file later
    do_list = []
    for index, rows in df.iterrows():
        area = rows['BBox Area']
        if (area >= 300000):
            do_list.append(1)
        elif (area <= 299999 and area >= 200000):
            do_list.append(2)
        elif (area <= 199999 and area >= 120000):
            do_list.append(3)
        elif (area <= 119999 and area >= 79800):
            do_list.append(4)
        else:
            do_list.append(5)

        df['Distance Offset'] = pd.Series(do_list)

    return df


def get_filelist(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


def declare_image_df(image_list):
    columns_image = [
    'Image Width',
    'Image Height'
    ]

    image_df = pd.DataFrame(columns = columns_image)

    image_meta = []

    for image_path in image_list: # I need to load each image name into a list
        im = Image.open(image_path)
        img_width = im.size[0]
        img_height = im.size[1]
        image_df.loc[len(image_df)]=[img_width, img_height]

    return image_df


def calculate_partitions(final_df):
    lb_list = []
    rb_list = []
    for index, rows in final_df.iterrows():
        distance_offset = rows['Distance Offset']
        original_width = rows['Image Width']
        if (distance_offset == 1):
            lb = original_width * 0.338414634
            rb = original_width * 0.664634146
        elif (distance_offset == 2):
            lb = original_width * 0.385670732
            rb = original_width * 0.625
        elif (distance_offset == 3):
            lb = original_width * 0.414634146
            rb = original_width * 0.599085366
        elif (distance_offset == 4):
            lb = original_width * 0.43445122
            rb = original_width * 0.585365854
        elif (distance_offset == 5):
            lb = original_width * 0.445121951
            rb = original_width * 0.570121951
        else:
            print("INVALID OFFSET")
            break
        lb_list.append(round(lb))
        rb_list.append(round(rb))
    final_df['Left Bound'] = lb_list
    final_df['Right Bound'] = rb_list
    return final_df


def determine_offsets(final_df):
    # Create and calculate offset_list using bounding comparisons with BBox coordinates
    offset_list = []
    for index, row in final_df.iterrows():
        if (row['BBox X-axis'] < row['Left Bound']):
            offset_list.append('Left')
        elif (row['BBox X-axis'] > row['Right Bound']):
            offset_list.append('Right')
        else:
            offset_list.append('Center')
    # Create 'Offset Factor' Column, and populate it using calculated offset-list values
    final_df['Offset Factor'] = offset_list
    return final_df


def retrieve_buffer_values(final_df):
    buffer_df = pd.read_csv('mdpfiles/predicted_output/decoded_raw.csv')
    final_df['Robot X-axis'] = buffer_df['x']
    final_df['Robot Y-axis'] = buffer_df['y']
    final_df['Camera Orientation'] = buffer_df['orientation']
    return final_df


def calculate_actual_coordinates(final_df):
    def calculate_relative_horizon(robot_value, orientation, offset_factor):
        if (orientation == 'UP'):
            if (offset_factor == 'Left'):
                robot_value -= 1
            elif (offset_factor == 'Right'):
                robot_value += 1
            elif (offset_factor == 'Center'):
                robot_value = robot_value
            else:
                print('Non-existent offset')
        elif (orientation == 'DOWN'):
            if (offset_factor == 'Left'):
                robot_value += 1
            elif (offset_factor == 'Right'):
                robot_value -= 1
            elif (offset_factor == 'Center'):
                robot_value = robot_value
            else:
                print('Non-existent offset')
        elif (orientation == 'LEFT'):
            if (offset_factor == 'Left'):
                robot_value -= 1
            elif (offset_factor == 'Right'):
                robot_value += 1
            elif (offset_factor == 'Center'):
                robot_value = robot_value
            else:
                print('Non-existent offset')
        elif (orientation == 'RIGHT'):
            if (offset_factor == 'Left'):
                robot_value += 1
            elif (offset_factor == 'Right'):
                robot_value -= 1
            elif (offset_factor == 'Center'):
                robot_value = robot_value
            else:
                print('Non-existent offset')
        else:
            print('HORIZON CALCULATION ERROR')
        return robot_value
    actual_x = []
    actual_y = []
    for index, row in final_df.iterrows():
        robot_x = row['Robot X-axis']
        robot_y = row['Robot Y-axis']
        distance_offset = row['Distance Offset']
        offset_factor = row['Offset Factor']
        orientation = row['Camera Orientation']
        if (orientation == 'UP'):
            calculated_y = robot_y + distance_offset
            calculated_x = calculate_relative_horizon(robot_x, orientation, offset_factor)
        elif (orientation == 'DOWN'):
            calculated_y = robot_y - distance_offset
            calculated_x = calculate_relative_horizon(robot_x, orientation, offset_factor)
        elif (orientation == 'LEFT'):
            calculated_x = robot_x - distance_offset
            calculated_y = calculate_relative_horizon(robot_y, orientation, offset_factor)
        elif (orientation == 'RIGHT'):
            calculated_x = robot_x + distance_offset
            calculated_y = calculate_relative_horizon(robot_y, orientation, offset_factor)
        else:
            print('ORIENTATION ERROR')
            break
        actual_x.append(calculated_x)
        actual_y.append(calculated_y)
    final_df['Actual Image X-axis'] = pd.Series(actual_x)
    final_df['Actual Image Y-axis'] = pd.Series(actual_y)
    return final_df


def map_actual_image_id(final_df):

    id_dict = {
        '[ID: 6] six': 6,
        '[ID: 7] seven' : 7,
        '[ID: 8] eight' : 8,
        '[ID: 9] nine' : 9,
        '[ID: 10] zero' : 10,
        '[ID: 11] Alphabet V' : 11,
        '[ID: 12] Alphabet W' : 12,
        '[ID: 13] Alphabet X' : 13,
        '[ID: 14] Alphabet Y' : 14,
        '[ID: 15] Alphabet Z' : 15,
        '[ID: 3] right arrow' : 3,
        '[ID: 5] Go' : 5,
        '[ID: 4] left arrow' : 4,
        '[ID: 2] down arrow' : 2,
        '[ID: 1] Up arrow' : 1
    }
    final_df['Actual Image ID'] = final_df['Description'].map(id_dict)
    return final_df


def declare_unique_df(final_df):
    unique_id_list = []
    unique_pathname_list = []
    unique_x_list = []
    unique_y_list = []
    for index, rows in final_df.iterrows():
        input_pathname = rows['Path Name']
        input_id = rows['Actual Image ID']
        input_x = rows['Actual Image X-axis']
        input_y = rows['Actual Image Y-axis']
        if (input_id not in unique_id_list):
            unique_pathname_list.append(input_pathname)
            unique_id_list.append(input_id)
            unique_x_list.append(input_x)
            unique_y_list.append(input_y)
    unique_df = pd.DataFrame()
    unique_df['Image Path'] = unique_pathname_list
    unique_df['Actual Image ID'] = unique_id_list
    unique_df['Actual Image X-axis'] = unique_x_list
    unique_df['Actual Image Y-axis'] = unique_y_list
    return unique_df


def declare_output_string(unique_df):

    output_df = unique_df[['Actual Image ID', 'Actual Image X-axis', 'Actual Image Y-axis']]
    output_string = 'ia'
    for index, row in output_df.iterrows():
        img_id = str(row['Actual Image ID'])
        img_x = str(row['Actual Image X-axis'])
        img_y = str(row['Actual Image Y-axis'])
        value_sequence = img_id+','+img_x+','+img_y+'|'
        output_string += value_sequence
    output_string = output_string[:-1] # code to remove last '|'
    #output_string += ';'
    return output_string #ia1,1,1|1,1,1|1,1,1|1,1,1|1,1,1
