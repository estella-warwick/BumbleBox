'''set up the tag tracking/recording schedule based on the settings in the setup.py script'''


import setup
from crontab import CronTab
import os

def find_file(file_name, directory_path):
    for dirpath, dirnames, fnames in os.walk(directory_path):
        for filename in fnames:
            if filename == file_name:
                return dirpath + '/' + file_name

'''find the path to the record_video file on the computer'''
record_video_path = find_file('record_video.py', '/home/pi')

'''make sure the computer recognizes the thumb drive or storage device when the computer turns on, and name it bumblebox'''
cron = CronTab(user='pi')
cron.remove_all()
job1 = cron.new(command='sudo mount /dev/sda1 /mnt/bumblebox -o umask=000')
job1.every_reboot()
cron.write()

'''make sure that we can write to this storage drive and to folders that we create on it'''
job1 = cron.new(command='sudo chmod -R ugo+rwx /mnt/bumblebox')
job1.every_reboot()
cron.write()

'''schedule the record video script to run every X minutes based on the recording_frequency variable in setup.py'''
job2 = cron.new(command=f'python3 {record_video_path} --data_folder_path {setup.data_folder_path} -t {setup.recording_time} -q {setup.quality} -fps {setup.frames_per_second} --shutter {setup.shutter_speed} -w {setup.width} -ht {setup.height} -d {setup.tag_dictionary} --box_type {setup.box_type} -cd {setup.codec} -tf {setup.tuning_file} -nr {setup.noise_reduction_mode} -z {setup.recording_digital_zoom}')
job2.minute.every(setup.recording_frequency)
cron.write()

'''if tag tracking is set to true, have tag tracking take place at an interval set by the tag_tracking_frequency variable in setup.py - if video recording and tag tracking fall on the same minute, video recording will override the tag tracking, and a video will be saved'''

if setup.tag_tracking == True:

    tag_tracking_path = find_file('ram_capture_tag_tracking.py', '/home/pi')


    minutes_list = {
        "1" : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59],
        "2" : [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58],
        "3" : [0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57],
        "4" : [0,4,8,12,16,20,24,28,32,36,40,44,48,52,56],
        "5" : [0,5,10,15,20,25,30,35,40,45,50,55],
        "6" : [0,6,12,18,24,30,36,42,48,54],
        "7" : [0,7,14,21,28,35,42,49,56],
        "8" : [0,8,16,24,32,40,48,56],
        "9" : [0,9,18,27,36,45,54],
        "10" : [0,10,20,30,40,50,60],
        "15" : [0,15,30,45],
        "20" : [0,20,40],
        "30" : [0, 30],
        "60" : [0]
    }

    for key, val in minutes_list.items():
     
        if str(setup.recording_frequency) == key:
            recording_minutes = val

        if str(setup.tag_tracking_frequency) == key:
            tag_tracking_minutes = val

    tag_tracking_without_recording_minutes = [ minute for minute in tag_tracking_minutes if minute not in recording_minutes]


    job3 = cron.new(command=f'python3 {tag_tracking_path} --data_folder_path {setup.data_folder_path} -t {setup.recording_time} -fps {setup.frames_per_second} --shutter {setup.shutter_speed} -w {setup.width} -ht {setup.height} -d {setup.tag_dictionary} -tf {setup.tuning_file} --box_type {setup.box_type} -nr {setup.noise_reduction_mode} -z {setup.recording_digital_zoom}')
    job3.minute.on(tag_tracking_without_recording_minutes[0])
    for minute in tag_tracking_without_recording_minutes[1:]:
        job3.minute.also.on(minute)

    cron.write()
