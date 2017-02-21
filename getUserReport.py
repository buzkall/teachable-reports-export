# -*- coding: utf-8 -*-
from operator import itemgetter

import requests
import sys
import shelve
import os.path

dir_path = os.path.dirname(os.path.realpath(__file__))
SECRETS_PATH = dir_path + '/secrets.py'
if os.path.exists(SECRETS_PATH):
    from secrets import username, password, site_url
else:
    print 'Missing secrets.py file with login data'
    sys.exit(1)


#### teachable urls

URL_COURSES = site_url+'/api/v1/courses'
URL_FIND_USER = site_url+'/api/v1/users?name_or_email_cont='
URL_REPORT_CARD = site_url+'/api/v1/users/USER_ID/report_card'
URL_CURRICULUM = site_url+'/api/v1/courses/COURSE_ID/curriculum'
#CACHE_PATH = '/tmp/teachable_cache.out'
CACHE_PATH = dir_path + '/teachable_cache.out'

#####

course_list = {}
user_report_card = {}
curriculum = []
course_curriculum = {}
output = []
user_name = ''


if len(sys.argv) > 1:
    user_mail = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = ''
else:
    print 'Missing user email as parameter'
    sys.exit(1)


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


def get_course_list():
    global course_list
    if 'courses' in cached:
        course_list = cached['courses']
    else:
        course_info = s.get(URL_COURSES).json()
        if course_info.get('error'):
            print 'Check Teachable credentials'
            sys.exit(1)
        else:
            course_list = course_info.get('courses')

        cached['courses'] = course_list
        print 'Courses were not previously in cache'


def get_user_report_card():
    global user_report_card, user_name
    users = s.get(URL_FIND_USER + user_mail).json()
    if users.get('error'):
        print 'Check Teachable credentials'
        sys.exit(1)

    if not users.get('users'):
        print 'There is no user with that email'
        sys.exit(1)
    else:
        user_id = str(users.get('users')[0].get('id'))
        user_name = users.get('users')[0].get('name').strip()
        url_user_report_card = URL_REPORT_CARD.replace('USER_ID', user_id)
        user_report_card = s.get(url_user_report_card).json()


def get_course_curriculum():
    global curriculum, course_curriculum

    url_course_curriculum = URL_CURRICULUM.replace('COURSE_ID', course_id)
    course_curriculum = s.get(url_course_curriculum).json().get('lecture_sections')
    if 'curriculum' in cached:
        curriculum = cached['curriculum']
        if course_id in curriculum:
            course_curriculum = curriculum[course_id]
        else:
            url_course_curriculum = URL_CURRICULUM.replace('COURSE_ID', course_id)
            course_curriculum = s.get(url_course_curriculum).json()
            curriculum.update({course_id: course_curriculum})
            cached['curriculum'] = curriculum
            print 'Curriculum of this course was not previously in cache'
    else:
        url_course_curriculum = URL_CURRICULUM.replace('COURSE_ID', course_id)
        course_curriculum = s.get(url_course_curriculum).json()
        curriculum = {course_id: course_curriculum}
        cached['curriculum'] = curriculum
        print 'Curriculum was not previously in cache'


def get_lecture_title():
    global course_curriculum

    if course.get('completed_lecture_ids'):
        course_curriculum = curriculum.get(course_id)
        sections = course_curriculum.get('lecture_sections')
        for section in sections:
            lecture_id = find(section.get('lectures'), 'id', course.get('completed_lecture_ids')[-1])
            if lecture_id >= 0:
                return section.get('lectures')[lecture_id].get('name')
    return ''


def get_section_title():
    global course_curriculum

    if course.get('completed_lecture_ids'):
        course_curriculum = curriculum.get(course_id)
        sections = course_curriculum.get('lecture_sections')
        for section in sections:
            lecture_id = find(section.get('lectures'), 'id', course.get('completed_lecture_ids')[-1])
            if lecture_id >= 0:
                return section.get('name')
    return ''


cached = shelve.open(CACHE_PATH)

s = requests.Session()
# get username and password from the secrets.py file
s.auth = (username, password)
s.headers.update({'x-test': 'true'})

get_course_list()
get_user_report_card()

for key, course in user_report_card.iteritems():
    course_id = str(course.get('course_id'))

    get_course_curriculum()
    course_data = find(course_list, 'id', int(course_id))
    current_lecture_title = get_lecture_title()
    current_section_title = get_section_title()

    output.append({'course_id': course_id,
                   'course_name': course_list[course_data].get('name'),
                   'course_percentage': course.get('percent_complete'),
                   'course_current_lecture': current_lecture_title,
                   'course_current_section': current_section_title})

user_ordered_list = sorted(output, key=itemgetter('course_percentage'), reverse=True)

if output_file:
    f = open(output_file, 'a')
    sys.stdout = f

print '###### Report of ' + user_name.encode('utf-8') + ' (' + user_mail.encode('utf-8') + ') #########'
for item in user_ordered_list:
    print 'Curso: ' + item.get('course_name').encode('utf-8') + ' - ' + \
          str(item.get('course_percentage')).encode('utf-8') + '%' + ' - ' + \
          'Sección: ' + item.get('course_current_section').encode('utf-8') + ' - ' + \
          'Lectura: ' + item.get('course_current_lecture').encode('utf-8')
print '###### end Report of ' + user_name.encode('utf-8') + ' (' + user_mail.encode('utf-8') + ') #########'

if output_file:
    print ' '
    f.close()
cached.close()
