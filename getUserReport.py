# -*- coding: utf-8 -*-
from operator import itemgetter

import requests
import sys
import shelve
import os.path
import time
import argparse

dir_path = os.path.dirname(os.path.realpath(__file__))
SECRETS_PATH = dir_path + '/secrets.py'
if os.path.exists(SECRETS_PATH):
    from secrets import username, password, site_url
else:
    print 'Missing secrets.py file with login data'
    sys.exit(1)

#### teachable urls
URL_COURSES = site_url + '/api/v1/courses'
URL_FIND_USER = site_url + '/api/v1/users?name_or_email_cont='
URL_REPORT_CARD = site_url + '/api/v1/users/USER_ID/report_card'
URL_CURRICULUM = site_url + '/api/v1/courses/COURSE_ID/curriculum'
URL_COURSE_PRICE = site_url + '/api/v1/courses/COURSE_ID/products'
# CACHE_PATH = '/tmp/teachable_cache.out'
CACHE_PATH = dir_path + '/teachable_cache.out'
MAXIMUM_CACHE_DURATION = 60 * 60 * 24 * 7  # One week
#####

course_list = {}
curriculum = {}
course_curriculum = {}
output = []

parser = argparse.ArgumentParser(description='''Get your student status in Teachable. ''', epilog="""---""")
parser.add_argument('--hidefree', type=int, default=1, help='0: show/1: hide free courses ')
parser.add_argument('email', type=str, nargs=1, default='', help='email')
parser.add_argument('output_file', nargs='?', default='', help='Output file')

args = parser.parse_args()

#print args

HIDE_FREE_COURSES = args.hidefree  # set to 0 to show all

# process position variables
output_file = ''
if args.output_file:
    output_file = args.output_file
    print 'Output will be saved to ' + output_file

user_mail = args.email[0]


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


def get_course_list():
    global course_list

    if 'courses' in cached_data:
        course_list = cached_data['courses']
    else:
        course_info = s.get(URL_COURSES).json()
        if course_info.get('error'):
            print 'Check Teachable credentials'
            sys.exit(1)
        else:
            course_list = course_info.get('courses')

        cached_data['courses'] = course_list
        print 'Courses were not previously in cache'


def get_course_price(course_id):
    url_course_price = URL_COURSE_PRICE.replace('COURSE_ID', course_id)
    course = s.get(url_course_price).json()
    return course.get('products')[0].get('price')


def get_user_name(user_mail):

    users = s.get(URL_FIND_USER + user_mail).json()
    if users.get('error'):
        print 'Check Teachable credentials'
        sys.exit(1)

    if not users.get('users'):
        print 'There is no user with that email'
        sys.exit(1)
    else:
        return users.get('users')[0].get('name').strip()


def get_user_report_card():

    users = s.get(URL_FIND_USER + user_mail).json()
    if users.get('error'):
        print 'Check Teachable credentials'
        sys.exit(1)

    if not users.get('users'):
        print 'There is no user with that email'
        sys.exit(1)
    else:
        user_id = str(users.get('users')[0].get('id'))
        url_user_report_card = URL_REPORT_CARD.replace('USER_ID', user_id)
        return s.get(url_user_report_card).json()


def get_course_curriculum(course_id):
    global curriculum, course_curriculum

    url_course_curriculum = URL_CURRICULUM.replace('COURSE_ID', course_id)
    course_curriculum = s.get(url_course_curriculum).json().get('lecture_sections')
    if 'curriculum' in cached_data:
        curriculum = cached_data['curriculum']
        if course_id in curriculum:
            course_curriculum = curriculum.get('course_id')

        else:
            get_new_course_curriculum()
            print 'Curriculum of this course was not previously in cache'
    else:
        get_new_course_curriculum()
        print 'Curriculum was not previously in cache'


def get_new_course_curriculum():
    global curriculum, course_curriculum

    url_course_curriculum = URL_CURRICULUM.replace('COURSE_ID', course_id)
    course_curriculum = s.get(url_course_curriculum).json()
    curriculum.update({course_id: course_curriculum})
    cached_data['curriculum'] = curriculum


def get_latest_viewed_title(course, course_id):
    global course_curriculum
    ordered_id_list = []

    if course.get('completed_lecture_ids'):
        course_curriculum = curriculum.get(course_id)
        sections = course_curriculum.get('lecture_sections')

        for section in sections:
            for lecture in section.get('lectures'):
                ordered_id_list.append(lecture.get('id'))

        completed_lectures = course.get('completed_lecture_ids')

        # this function to order the completed_lectures looks,
        # but will fail if one of the lectures gets deleted (and won't appear in ordered_id_list)
        #ordered_completed_lectures = sorted(completed_lectures, key=ordered_id_list.index)
        ordered_completed_lectures = sorted(completed_lectures,
                                            key=lambda k: (ordered_id_list.index(k) if k in ordered_id_list else -1))

        for section in sections:
            lecture_id = find(section.get('lectures'), 'id', ordered_completed_lectures[-1])
            if lecture_id >= 0:
                lecture_name = section.get('lectures')[lecture_id].get('name')
                section_name = section.get('name')
                return lecture_name, section_name
    return '', ''


def expire_cache():
    if os.path.isfile(CACHE_PATH):
        cache_antiquity = time.time() - os.path.getctime(CACHE_PATH)
        if cache_antiquity > MAXIMUM_CACHE_DURATION:
            os.remove(CACHE_PATH)
            print('Cache file dumped!')


def generate_student_progress_list(course, course_id):
    get_course_curriculum(course_id)
    course_data = find(course_list, 'id', int(course_id))
    current_lecture_title, current_section_title = get_latest_viewed_title(course, course_id)
    output.append({'course_id': course_id, 'course_name': course_list[course_data].get('name'),
                   'course_percentage': course.get('percent_complete'), 'course_current_lecture': current_lecture_title,
                   'course_current_section': current_section_title})


def generate_output(users_mail):

    user_name = get_user_name(users_mail)
    user_report_card = get_user_report_card()

    for key, course in user_report_card.iteritems():
        course_id = str(course.get('course_id'))

        if HIDE_FREE_COURSES:
            if get_course_price(course_id) > 0:
                generate_student_progress_list(course, course_id)
        else:
            generate_student_progress_list(course, course_id)

    user_ordered_list = sorted(output, key=itemgetter('course_percentage'), reverse=True)
    if output_file:
        f = open(output_file, 'a')
        sys.stdout = f
    print '###### Report of ' + user_name.encode('utf-8') + ' (' + user_mail.encode('utf-8') + ') #########'
    counter = 1
    for item in user_ordered_list:
        if item.get('course_percentage') == 0:
            print str(counter) + ' - Curso: ' + item.get('course_name').encode('utf-8') + ' - ' + str(
                item.get('course_percentage')).encode('utf-8') + '%'
        else:
            print str(counter) + ' - Curso: ' + item.get('course_name').encode('utf-8') + ' - ' + str(
                item.get('course_percentage')).encode('utf-8') + '%' + ' - ' + 'Sección: ' + item.get(
                'course_current_section').encode('utf-8') + ' - ' + 'Lectura: ' + item.get(
                'course_current_lecture').encode(
                'utf-8')
        counter += 1
    print '###### end Report of ' + user_name.encode('utf-8') + ' (' + user_mail.encode('utf-8') + ') #########'
    if output_file:
        print ' '
        f.close()


cached_data = shelve.open(CACHE_PATH)

s = requests.Session()
# get username and password from the secrets.py file
s.auth = (username, password)
s.headers.update({'x-test': 'true'})

get_course_list()

generate_output(user_mail)

cached_data.close()
