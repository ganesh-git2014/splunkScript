import urllib2
import json
from pprint import pprint
from datetime import datetime

MAX_RESULT = 1000

class RestInPeace(object):
    '''
    '''

    URI_BASE = '/rest/api/latest'
    PROJECT_URI = URI_BASE + '/project/{project_id}.json'
    PLAN_URI = URI_BASE + '/plan/{plan_id}.json'
    RESULT_URI = URI_BASE + '/result/{plan_id}.json'

    def __init__(self, bamboo_host):
        self.host = bamboo_host

    def get_url(self, uri, expand, max_result):
        '''
        get the url to open
        '''
        if expand is not None:
            expand = expand if isinstance(expand, str) else ",".join(expand)

        uri = uri + '?max-result=' + str(max_result)
        uri = uri + '&expand=' + expand if expand is not None else uri
        return self.host + uri

    # for projects
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

    def get_all_plans_of_project(self, project_id):
        '''
        get all plans of the givent project

        @param project_id: the id of the project to get
        @type project_id: string

        @return: all the plans of the project
        @rtype: list of dictionary
        '''
        resp = json.loads(self.get_project(project_id, expand=['plans',]))
        ret = []
        for plan in resp['plans']['plan']:
            p = {}
            p['key'] = plan['key']
            p['name'] = plan['name']
            p['enabled'] = plan['enabled']
            ret.append(p)
        return ret

    # for plans
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

    def get_all_variables_of_plan(self, plan_id):
        '''
        Get all the bamboo variables of the given plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @return: the bamboo variables of the plan
        @rtype: dictionary
        '''
        resp = json.loads(
            self.get_plan(plan_id=plan_id, expand=['variableContext', ]))

        ret = {}
        for variable in resp['variableContext']['variable']:
            ret[variable['key']] = variable['value']
        return ret

    def get_variable_of_plan(self, plan_id, variable):
        '''
        Get the bamboo variable of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @param variable: the name of the variable
        @type variable: string

        @return: the value of the variable
        @rtype: string
        '''
        variables = self.get_all_variables_of_plan(plan_id)
        try:
            return variables[variable]
        except KeyError, err:
            print 'Can not find the variable: {v}'.format(v=variable)
            print err

    def get_branch_of_plan(self, plan_id):
        '''
        get the owner of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @return: the splunk branch of the given plan
        @rtype: string
        '''
        return self.get_variable_of_plan(plan_id, 'BRANCH')

    def get_owner_of_plan(self, plan_id):
        '''
        get the owner of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @return: the owner of the given plan
        @rtype: string
        '''
        return self.get_variable_of_plan(plan_id, 'SusQA')

    def get_build_name_of_plan(self, plan_id, branch=False):
        '''
        get the build name of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @param branch: the plan is a branch plan or not
        @type branch: boolean

        @return: the build name of the given plan
        @rtype: string
        '''
        resp = json.loads(self.get_plan(plan_id))
        if branch:
            return resp['master']['shortName']
        else:
            return resp['buildName']

    def get_other_branches_of_plan(self, plan_id):
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
                b['enabled'] = branch['enabled']
                ret.append(b)
            return ret
        except KeyError, err:
            return []

    # for results
    def get_result(self, plan_id, expand=None, max_result=MAX_RESULT):
        '''
        get the information of the given plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @param expand: the objects to expand
        @type expand: list of strings

        @param max_result: maximum result to get from bamboo
        @type max_result: integer
        '''
        url = self.get_url(self.RESULT_URI.format(plan_id=plan_id), expand,
            max_result)
        return urllib2.urlopen(url).readlines()[0]

    def get_latest_result(self, plan_id):
        '''
        Get the last test result of the plan

        @param plan_id: the id of the plan to get
        @type plan_id: string

        @return: the test result of the plan
        @rtype: dictionary
        '''
        resp = json.loads(self.get_result(plan_id, expand='results.result'))
        result = resp['results']['result'][0]

        fields = ['successfulTestCount', 'failedTestCount',
                  'quarantinedTestCount', 'buildReason', 'vcsRevisionKey',
                  'prettyBuildCompletedTime', 'buildDurationInSeconds',
                  'planName', 'projectName']
        ret = {}
        for field in fields:
            ret[field] = result[field]
        ret['branch'] = self.get_branch_of_plan(plan_id)
        return ret

rest = RestInPeace('http://bamboo.splunk.com')

result = {}
start = datetime.now()
for plan in rest.get_all_plans_of_project('CUPCAKE'):
    if plan['enabled']:
        # get result for the default branch
        result_key = rest.get_branch_of_plan(plan['key']) + rest.get_build_name_of_plan(plan['key'])
        result[result_key] = rest.get_latest_result(plan['key'])

        # get result for all other branch
        for branch in rest.get_other_branches_of_plan(plan['key']):
            if branch['enabled']:
                result_key = rest.get_branch_of_plan(branch['key']) + rest.get_build_name_of_plan(branch['key'], branch=True)
                result[result_key] = rest.get_latest_result(plan['key'])
    else:
        print '{p} is disabled'.format(p=plan['name'])

end = datetime.now()
diff = end - start
print diff.seconds