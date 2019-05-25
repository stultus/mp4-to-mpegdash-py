# mp4-to-mpegdash-py
Python Script to convert a MP4 file into onDemand MPEG-DASH
## Dependencies 
* ffmpeg - https://www.ffmpeg.org/ 
* MP4Box - https://gpac.wp.mines-telecom.fr/mp4box/

## Installation
### On Linux
`$ sudo apt-get install ffmpeg`</br>
`$ sudo apt-get install gpac`

### On Mac
`$ brew install ffmpeg`</br>
`$ brew install MP4Box`
* ffmpeg version 4.1.3
* MP4Box - GPAC version 0.7.1

## Usage 
`$ python transcode.py $FILENAME`

### Acknowledgements 
This script is inspired from https://github.com/Cloudoki/mp4-to-mpegdash
