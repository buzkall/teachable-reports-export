# Teachable Reports export
Export the report of your Teachable students using the unofficial Teachable API

Teachable.com doesn't have an official API to export your students data.   

It has some webhooks to trigger events and use them with services like Zapier, but there is no fast and practical solution to see your students reports, especially if you need to check multiple students.
The website is done using Angular, and needs some api urls to load the content, so I've created a script to collect all the data of all the courses a specific student is enrolled in to make things faster and less time consuming.

<p align="center">
    <img src="http://i.imgur.com/WpLZ9ce.png" alt="teachable_schema">
</p>

## Config
This script has been tested with python 2.7

It requires the module "request" which can be installed using:

    pip install requests

You should copy the file called secrets_example.py, rename it as secrets.py and set your username, password and yout teachable custom domain

    username='YOUR_TEACHABLE_USERNAME'
    password='YOUR_TEACHABLE_PASSWORD'
    site_url='http://YOUR_TEACHABLE_URL'


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

Specifying the output file won't output anything to the screen and will save it into a file:

    python getUserReport.py STUDENT_EMAIL FILENAME.txt
    
The hidefree parameter is set to 1 by default (will hide all the free courses).
Adding --hidefree=0 will display all paid and free courses.

## Cache and rate limits
To avoid reaching any rate limit, the script caches the courses' data into a file using Shelve.  
The cache path can be changed modifying the variable CACHE_PATH, by default it creates a file called teachable_cache.out in the same folder

The cache file expires in a week, but this time can be changed modifying the constant MAXIMUM_CACHE_DURATION.
