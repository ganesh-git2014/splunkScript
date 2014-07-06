import urllib2
import json
from pprint import pprint

MAX_RESULT = 1000

class RestInPeace(object):
    '''
    '''

    URI_BASE = '/rest/api/latest'
    PROJECT_URI = URI_BASE + '/project/{project_id}.json'
    PLAN_URI = URI_BASE + '/plan/{plan_id}.json'

    def __init__(self, bamboo_host):
        self.host = bamboo_host

    def get_url(self, uri, expand, max_result):
        '''
        get the url to open
        '''
        uri = uri + '?max_result=' + str(max_result)
        uri = uri + '&expand=' + ",".join(expand) if expand is not None else uri
        return self.host + uri

    def get_project(self, project_id, expand=None, max_result=MAX_RESULT):
        '''
        get the information of given project

        @param project_id: the id of the project to get
        @type project_id: string

        @param expand: the objects to expand
        @type expand: list of strings

        @param max_result: maximum result to get from bamboo
        @type max_result: integer
        '''
        url = self.get_url(self.PROJECT_URI.format(project_id=project_id),
            expand, max_result)
        return urllib2.urlopen(url).readlines()[0]

    def get_plan(self, plan_id, expand=None, max_result=MAX_RESULT):
        '''
        get the information of the given plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @param expand: the objects to expand
        @type expand: list of strings

        @param max_result: maximum result to get from bamboo
        @type max_result: integer
        '''
        url = self.get_url(self.PLAN_URI.format(plan_id=plan_id), expand,
            max_result)
        return urllib2.urlopen(url).readlines()[0]

    def get_plan_owner(self, plan_id):
        '''
        get the owner of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @return: the owner of the given plan
        @rtype: string
        '''
        resp = json.loads(
            self.get_plan(plan_id=plan_id, expand=['variableContext', ]))
        for variable in resp['variableContext']['variable']:
            if variable['key'] == 'SusQA':
                return variable['value']
        raise Exception, ('Can not find the owner,'
            'this plan does not have "SusQA" variable')

    def get_plan_branch(self, plan_id):
        '''
        get the owner of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @return: the splunk branch of the given plan
        @rtype: string
        '''
        resp = json.loads(
            self.get_plan(plan_id=plan_id, expand=['variableContext', ]))
        for variable in resp['variableContext']['variable']:
            if variable['key'] == 'BRANCH':
                return variable['value']
        raise Exception, ('Can not find the branch,'
            'this plan does not have "BRANCH" variable')

    def get_plan_other_branches(self, plan_id):
        '''
        Get branches of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @return: list of other branches that this plan have
        @rtype: list of dictionary
        '''
        resp = json.loads(
            self.get_plan(plan_id=plan_id, expand=['branches', ]))
        try:
            ret = []
            for branch in resp['branches']['branch']:
                b = {}
                b['key'] = branch['key']
                b['name'] = branch['name']
                ret.append(b)
            return ret
        except KeyError, err:
            print err
            print 'branches is probably not found on this branch'

rest = RestInPeace('http://bamboo')
a = rest.get_project('CUPCAKE', expand=['plans', ])
b = rest.get_plan('CUPCAKE-ADMONITOR', expand=['branches','variableContext'])