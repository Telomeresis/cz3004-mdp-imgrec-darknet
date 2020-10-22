import os
import glob
os.system
import PIL
import PIL.Image as Image
import time


def run_darknet():

    dd_cmd = ['explorer mdpfiles\\predicted_output']
    initial_cmd = 'darknet.exe detector batch '
    data_cmd    = 'mdpfiles\obj.data '
    cfg_cmd     = 'mdpfiles\yolov4-obj.cfg '
    weights_cmd = 'mdpfiles\yolov4-obj_bestb.weights '
    threshold_cmd = '-thresh 0.90 '
    io_cmd      = 'io_folder mdpfiles/samples/ mdpfiles/predicted_output/ '
    json_cmd    = 'output/ -out mdpfiles/predicted_output/result.json '
    result_cmd  = '-ext_output > mdpfiles/predicted_output/result.txt'
    dn_cmd = [initial_cmd + data_cmd + cfg_cmd + weights_cmd + threshold_cmd + io_cmd + json_cmd + result_cmd]
    os.system(' '.join(dd_cmd))
    os.system(' '.join(dn_cmd))


while (True):
    file_list = os.listdir(f'C:/Users/SAMARITAN/git/darknet/mdpfiles/samples')
    number_files = len(file_list)
    if (number_files >= 15):
        break
    time.sleep(2)

run_darknet()
