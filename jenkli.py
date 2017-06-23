#! /usr/bin/env python
import os
import jenkins
import termcolor
import argparse
import json
# import tabulate

jenkins_url = os.getenv('JENKINS_URL')
jenkins_user = os.getenv('JENKINS_USER')
jenkins_pwd = os.getenv('JENKINS_PWD')

def check_credentials():
    undefined = []
    undefined.append('JENKINS_URL' if not jenkins_url else '')
    undefined.append('JENKINS_USER' if not jenkins_user else '')
    undefined.append('JENKINS_PWD' if not jenkins_pwd else '')
    undefined = [v for v in undefined if v]
    if undefined:
        print 'Following env variables required but not set:', undefined
        return False
    else:
        return True

def connect_jenkins_server():
    s = jenkins.Jenkins(jenkins_url, username=jenkins_user, password=jenkins_pwd, timeout=5)
    return s

def check():
    s = connect_jenkins_server()
    me = s.get_whoami()
    print 'connected as', me['fullName']

def show_job_history(cmd_args):
    job_name = cmd_args[0]
    server = connect_jenkins_server()
    builds = server.get_job_info(job_name, fetch_all_builds=True, depth=0)['builds']
    builds = [server.get_build_info(job_name, number=b['number']) for b in builds[:5]]
    for b in builds:
        print_build_info(b)

# "timestamp": 1487089931022,
# "duration": 11440726,
        # "actions": [
        #     {
        #         "causes": [
        #             {
        #                 "shortDescription": "Started by user tomasz.lasica",
        #                 "userId": "tomasz.lasica",
        #                 "userName": "tomasz.lasica"
        #             }
        #         ]
        #     },
            # {
            #     "failCount": 63,
            #     "skipCount": 49,
            #     "totalCount": 425,
            #     "urlName": "testReport"
            # },

RESULT_COLORS = {
    'SUCCESS': 'green',
    'UNSTABLE': 'yellow',
    'FAILURE': 'red'
}

def result_color(result):
    return RESULT_COLORS.get(result) or 'white'

def find_key_in_list(dict_list, key):
    return [x[key] for x in dict_list if key in x]


def print_build_info(build_info):
    colored = []
    colored.append((build_info['displayName'], result_color(build_info['result'])))
    parameters = build_info['actions'][0]
    print build_info['actions']
    print find_key_in_list(build_info['actions'], 'causes')
    for text, color in colored:
        print termcolor.colored('{:<5}'.format(text), color),
        print '{:5.4}'.format(build_info['result']),

def description():
    return """
    Simple console jenkins client. Supported commands:
    check           checks if connection works
    describe <job>  describes job with given name
    show <job>      show all builds for given job name

    Examples:
    jenkli show QA2_Search_Workload
    jenkli run QA2_Search_Workload VERSION=5.1.0 CLUSTER_SIZE=3
    """

def main():
    parser = argparse.ArgumentParser(description=description(), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('cmd', type=str, help="command: check, describe, show, run")
    args, unknown_args = parser.parse_known_args()

    if not check_credentials():
        return 1

    if args.cmd == 'check':
        check()
    elif args.cmd in ['show', 'history', 'builds']:
        show_job_history(unknown_args)
    else:
        print 'Unknown command', args.cmd

if __name__ == "__main__":
    main()
