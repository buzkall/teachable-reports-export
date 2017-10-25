# Teachable Reports export
Export the report of your Teachable students using the unofficial Teachable API

Teachable.com doesn't have an official API to export your students data.   

It has some webhooks to trigger events and use them with services like Zapier, but there is no fast and practical solution to see your students reports, especially if you need to check multiple students.
The website is done using Angular, and needs some api urls to load the content, so I've created a script to collect all the data of all the courses a specific student is enrolled in to make things faster and less time consuming.

 
<p align="center">
    <img src="https://i.imgur.com/GFUNA3D.png" alt="teachable_schema">
</p>

## Install and Config
This script has been tested with python 2.7

It requires the module "request" which can be installed using:

    pip install requests
    
If you don't have pip installed you can do it with

    sudo easy_install pip
    
if pip install requests shows an error about urllib3 you can install it with

    sudo easy_install requests

After that you should copy the file called secrets_example.py, rename it as secrets.py and set your username, password and yout teachable custom domain

    username='YOUR_TEACHABLE_USERNAME'
    password='YOUR_TEACHABLE_PASSWORD'
    site_url='https://YOUR_TEACHABLE_URL'

It's important to set the site_url with https if your site uses https, otherwise when you run the script, you will get an error like this

    raise SSLError(e, request=request) requests.exceptions.SSLError: 
    HTTPSConnectionPool(host='xxxx', port=443): 
    Max retries exceeded with url: xxxxx 
    (Caused by SSLError(SSLError(1, u'[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] 
    sslv3 alert handshake failure (_ssl.c:590)'),)) 

## Usage

Typing --help will show the parameters info

    usage: getUserReport.py [-h] [--hidefree HIDEFREE] [-l LIST]
                        email [output_file]

    Get your student status in Teachable.

    positional arguments:
        emails                emails separated with commas
        output_file           Output file

    optional arguments:
    -h, --help            show this help message and exit
    --hidefree HIDEFREE   0: show/1: hide free courses
    
    
It should receive at least one parameter: the student's email  
The second parameter it's optional, and it's a filename in which the output data will be saved (if set, otherwise,
output will be echoed in terminal)

    python getUserReport.py STUDENT_EMAIL

It will output something like this

    ###### Report of STUDENT NAME (STUDENT EMAIL) #########
    COURSE1 NAME - 100% - LAST SECTION OF THE COURSE
    COURSE2 NAME - 62% - CURRENT SECTION OF THE COURSE
    COURSE3 NAME - 0% -
    ###### end Report of STUDENT NAME (STUDENT EMAIL) #########

You can pass the array several emails separated with commas

    python getUserReport.py STUDENT_EMAIL1,STUDENT_EMAIL2

Specifying the output file won't output anything to the screen and will save it into a file:

    python getUserReport.py STUDENT_EMAIL FILENAME.txt
    
The hidefree parameter is set to 1 by default (will hide all the free courses).
Adding --hidefree=0 will display all paid and free courses.

## Cache and rate limits
To avoid reaching any rate limit, the script caches the courses' data into a file using Shelve.  
The cache path can be changed modifying the variable CACHE_PATH, by default it creates a file called teachable_cache.out in the same folder

The cache file expires in a week, but this time can be changed modifying the constant MAXIMUM_CACHE_DURATION.
