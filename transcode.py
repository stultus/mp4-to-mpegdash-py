#! /usr/bin/python
''' Depends on ffmpeg and MP4Box. This scripts accepts a HD video and creates different
bitrate versions for dash
@author : Hrishikesh Bhaskaran <hrishi.kb@gmail.com>, May 2019
'''
import os
import sys
from xml.dom import minidom
try:
    import boto3
    from datetime import datetime

    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Videos will not be uploaded to S3")

config = {
    'keyint': '59',
    'framerate': '30000/1001',
    'profile': 'onDemand',
    'chunk': '1000',
}
base_filename = None
# pre-defined resolutions
versions = ['256', '426', '854', '1280', '1920']

files_to_clean = []
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
bucket_name = os.getenv('S3_BUCKET_NAME')
region = os.getenv('AWS_REGION')
def create_multiple_bitrate_versions(filename):
    for version in versions:
        command = 'ffmpeg -i {} -vf "hqdn3d,detelecine,yadif,scale={}:-2" -x264-params "keyint={}:min-keyint={}:no-scenecut" -strict -2 -preset veryfast -crf 25 -r {} {}/{}-{} -y'.format(
            filename, version, config.get('keyint'), config.get('keyint'),
            config.get('framerate'), base_filename, version, filename)
        print(command)
        os.system(command)


def create_multiple_segments(filename):
    os.chdir(base_filename)
    base_command = "MP4Box -dash {} -frag {} -rap -frag-rap -profile {} {} {}-{}{}"
    for version in versions:
        command = base_command.format(
            config.get('chunk'),
            config.get('chunk'),
            config.get('profile'),
            '-out ' + version + '-' + base_filename + '.mpd',
            version,
            filename,
            '#video',
        )
        print(command)
        os.system(command)
        files_to_clean.append(base_filename + '/' + version + '-' +
                              base_filename + '.mpd')
    command = base_command.format(
        config.get('chunk'),
        config.get('chunk'),
        config.get('profile'),
        '-out audio.mpd',
        versions[-1:][0],
        filename,
        '#audio',
    )
    print(command)
    os.system(command)
    files_to_clean.append(base_filename + '/' + 'audio.mpd')
    os.chdir('..')


def merge_mpds():
    root = None
    for mpd in files_to_clean:
        if not root:
            root = minidom.parse(mpd).documentElement
            continue
        period_element = root.childNodes[3]
        current_mpd_root = minidom.parse(mpd).documentElement
        adaption_set = current_mpd_root.childNodes[3].childNodes[1]
        period_element.appendChild(adaption_set)
    with open(base_filename + "/" + base_filename + ".mpd", 'w') as f:
        f.write(root.toxml())

def upload_to_s3(bucket=None):
    if bucket:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_ACCESS_SECRET_KEY,
            )
        for filename in os.listdir(base_filename):
            file = base_filename+"/"+filename
            date = datetime.date(datetime.now()).strftime("%d%m%Y")
            file_path = date + "/" + file
            with open(file, "rb") as f:
                s3_client.upload_fileobj(f, bucket, file_path)
            if filename.split('.')[-1] == "mpd":
                print(" \033[1;32;40m https://s3.{}.amazonaws.com/{}/{}".format(region,bucket,file_path))

if len(sys.argv) == 1:
    print("Enter the filename")
else:
    filename = sys.argv[1]
    if (' ' in filename):
        new_name = filename.replace(" ","-")
        os.rename(filename, new_name)
        filename = new_name
    base_filename = filename.split('.')[0]
    # create output file directory
    try:
        os.mkdir(base_filename)
    except FileExistsError:
        pass
    create_multiple_bitrate_versions(filename)
    create_multiple_segments(filename)
    merge_mpds()  
    # cleanup
    for file_name in files_to_clean:
        print('rm ' + file_name)
        os.remove(file_name)
    # upload to s3
    upload_to_s3(bucket_name)
