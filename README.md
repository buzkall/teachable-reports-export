# Teachable Reports export
Export your Teachable students' report using the unofficial Teachable API

Teachable.com doesn't have an official API to export your students data.   
It has some webhooks to trigger events and use them with services like Zapier, but there is no solution to get one of your studens report.  
The website is done using Angular, and it calls to some api urls to load the content, so I've created a script to get the data of all the courses a student is enrolled.

### Config
It's done using python 2.7  
You should rename the file called secrets_example.py to secrets.py and set your username, password and teachable custom domain

    username='YOUR_TEACHABLE_USERNAME'
    password='YOUR_TEACHABLE_PASSWORD'
    site_url='http://YOUR_TEACHABLE_URL'


### Usage
It should receive at least one parameter: the student's email  
The second parameter it's optional, and it's a filename in which the output data will be saved, if set

    python getUserReport.py STUDENT_EMAIL

It will output something like this

    ###### Report of STUDENT NAME (STUDENT EMAIL) #########
    COURSE1 NAME - 100% - LAST SECTION OF THE COURSE
    COURSE2 NAME - 62% - CURRENT SECTION OF THE COURSE
    COURSE3 NAME - 0% -
    ###### end Report of STUDENT NAME (STUDENT EMAIL) #########

Specifing the output file won't output anything to the screen and will save it into a file:

    python getUserReport.py STUDENT_EMAIL FILENAME.txt

To avoid reaching any rate limit, the script caches the courses' data into a file using Shelve.  
The cache path can be changed modifying the variable CACHE_PATH, by default it creates a file called teachable_cache.out in the same folder
