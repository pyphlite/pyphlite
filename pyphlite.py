from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import requests
import time

logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')

def dict_except(d, blocked_keys):
    ret = {}
    for k in d.keys():
        if k in blocked_keys:
            ret[k] = '...'
        else:
            ret[k] = d[k]
    return ret

class PhBase(object):
    def __init__(self, api_key, thin=False, jdata=None, req_params=None, **kwargs):
        logging.debug('PhBase.__init__(self, api_key="%s", thin="%s", initial_jdata="%s", req_params="%s", kwargs="%s").' %
                      (api_key, thin, ('' if jdata is None else '...'), req_params, dict_except(kwargs, 'jdata')))
        self._api_key = api_key
        self._thin = thin
        self._params = kwargs
        self._req_params = req_params

        if jdata is not None:
            self.update(jdata=jdata)
        elif not thin:
            self.update()

    def __repr__(self):
        return '<PhBase(api_key="%s")>' % self._api_key

    def update(self, jdata=None):
        logging.debug('PhBase.update(self, jdata="%s").' % ('' if jdata is None else '...'))
        self._thin = False #reminder: set thin to false
        raise NotImplemented

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:

            logging.debug('PhBase.__getattribute__(self, name="%s"): Not Found.' % name)

            if name == '_thin':
                raise AttributeError

            if self._thin:
                raise Warning('Attempted to access a non-existance attribute "%s" of a thin object. Running update()...' % name)
                logging.debug('PhBase.__getattribute__(self, name="%s"): Running update...' % name)
                self.update()
                self._thin = False #make sure!

            try:
                retval = self._jdata[name]
                logging.debug('PhBase.__getattr__(self, name="%s"): Found in _jdata.' % name)
                return retval
            except:
                logging.debug('PhBase.__getattr__(self, name="%s"): Not found in _jdata.' % name)
                return object.__getattribute__(self, name)

    def _get_req_params(self, req_params=None, default_value=None):
        if req_params is not None:
            return req_params
        elif self._req_params is not None:
            return self._req_params
        elif default_value is not None:
            return default_value
        else:
            return {}

class PhAccount(PhBase):
    def __init__(self, api_key, **kwargs):
        logging.info('PhAccount.__init__(self, api_key="%s", kwargs="%s").' %
                     (api_key, dict_except(kwargs, 'jdata')))
        super(self.__class__, self).__init__(api_key, **kwargs) 
        
    def __repr__(self):
        return '<PhAccount(api_key="%s")>' % self._api_key
    
    def update(self, jdata=None):
        logging.debug('PhAccount.update(self, jdata="%s").' % '...')
        self.list_all_projects(jdata=jdata, **(self._params))
        self._thin = False
        return self

    ### DIRECT API FUNCTIONS ###

    #Account-Level Functions
    def list_all_projects(self, jdata=None, req_params=None, **params):
        logging.info('PhAccount.list_all_projects(self, jdata="%s", req_params="%s", params="%s").' %
                     (('' if jdata is None else '...'), req_params, params))
        if jdata is None:
            params['api_key'] = self._api_key
            req_params = self._get_req_params(req_params)
                    
            logging.debug('PhAccount.list_all_projects: Requesting with params="%s", req_params="%s".' %
                          (params, req_params))
            
            req = requests.get(
                'https://www.parsehub.com/api/v2/projects', #list all projects
                params=params,
                **(req_params)
            )

            req.raise_for_status()
            jdata = json.loads(req.text)

        self._jdata = jdata
        self._thin = False #in case the user calls get_projects but not update() on a thin object
        
        logging.debug('PhAccount.list_all_projects: Parsing project list...')
        self.projects = [
            PhProject(self._api_key, proj_jdata['token'], thin=True, jdata=proj_jdata)
            for proj_jdata in jdata['projects']
        ]
        logging.debug('PhAccount.list_all_projects: ... Done.')
        return self.projects

    #Project-Level Functions
    def get_a_project(self, project_token, **kwargs):
        return PhProject(self._api_key, project_token, **kwargs)
    
    def run_a_project(self, project_token, **kwargs):
        return PhProject(self._api_key, project_token, thin=True).run(**kwargs)
    
    def get_last_ready_data(self, project_token, **kwargs):
        return PhProject(self._api_key, project_token, thin=True).get_last_ready_data(**kwargs)

    #Run-Level Functions
    def get_a_run(self, run_token, **kwargs):
        return PhRun(self._api_key, run_token, **kwargs)
    
    def get_data_for_a_run(self, run_token, **kwargs):
        return PhRun(self._api_key, run_token, thin=True).get_data(**kwargs)
    
    def cancel_a_run(self, run_token, **kwargs):
        return PhRun(self._api_key, run_token, thin=True).cancel(**kwargs)
    
    def delete_a_run(self, run_token, **kwargs):
        return PhRun(self._api_key, run_token, thin=True).delete(**kwargs)
    
class PhProject(PhBase):
    def __init__(self, api_key, project_token, **kwargs):
        logging.info('PhProject.__init__(self, api_key="%s", project_token="%s", kwargs="%s").' %
                     (api_key, project_token, dict_except(kwargs, 'jdata')))
        self._project_token = project_token
        super(self.__class__, self).__init__(api_key, **kwargs)
        
    def __repr__(self):
        title_s = ''
        if hasattr(self, '_jdata') and self._jdata.has_key('title'):
            title_s = ', title="%s"' % self._jdata['title']
        return '<PhProject(api_key="%s", project_token="%s"%s)>' % (self._api_key, self._project_token, title_s)

    def update(self, jdata=None):
        logging.info('PhProject.update(self, jdata="%s").' % ('' if jdata is None else '...'))
        if jdata is None:
            params = self._params
            params['api_key'] = self._api_key
            req_params = self._get_req_params()
            
            logging.debug('PhProject.update: Requesting with params="%s", req_params="%s".' %
                          (params, self._req_params))
            
            req = requests.get(
                'https://www.parsehub.com/api/v2/projects/%s' % #get a project
                self._project_token,
                params=params,
                **(req_params)
            )

            req.raise_for_status()
            jdata = json.loads(req.text)

        self._jdata = jdata
        self._thin = False

        try:
            logging.debug('PhProject.update: Attempting to create last_run object...')
            lr_jdata = jdata['last_run']
            self.last_run = PhRun(self._api_key, lr_jdata['run_token'], thin=True, jdata=lr_jdata)
            logging.debug('PhProject.update: ... Success!')
        except Exception as e:
            logging.debug('PhProject.update: Error: "%s"' % e)

        try:
            logging.debug('PhProject.update: Attempting to create last_ready_run object...')
            lrr_jdata = jdata['last_ready_run']
            self.last_ready_run = PhRun(self._api_key, lrr_jdata['run_token'], thin=True, jdata=lrr_jdata)
            logging.debug('PhProject.update: ... Success!')
        except Exception as e:
            logging.debug('PhProject.update: Error: "%s"' % e)

        try:
            logging.debug('PhProject.update: Attempting to create run_list object...')
            self.run_list = [
                PhRun(self._api_key, run_jdata['run_token'], thin=True, jdata=run_jdata)
                for run_jdata in jdata['run_list']
            ]
            logging.debug('PhProject.update: ... Success!')
        except Exception as e:
            logging.debug('PhProject.update: Error: "%s"' % e)

        

    def run(self, req_params=None, **kwargs):
        logging.info('PhProject.run(self, req_params="%s", kwargs="%s").' %
                     (req_params, dict_except(kwargs, 'jdata')))
        params = kwargs
        params['api_key'] = self._api_key
        req_params = self._get_req_params(req_params)
        
        logging.debug('PhProject.run: Request(project_token="%s", params="%s", req_params="%s"'
                      % (self._project_token, params, req_params))
        
        req = requests.post(
            'https://www.parsehub.com/api/v2/projects/%s/run' % #run a project
            self._project_token,
            params=params,
            **(req_params)
        )

        req.raise_for_status()
        req_jdata = json.loads(req.text)
        return PhRun(self._api_key, req_jdata['run_token'], thin=True, jdata=req_jdata)
    
    def get_last_ready_data(self, req_params=None, **kwargs):
        logging.info('PhProject.get_last_ready_data(self, req_params="%s", kwargs="%s").' %
                     (req_params, dict_except(kwargs, 'jdata')))
        params = kwargs
        params['api_key'] = self._api_key
        req_params = self._get_req_params(req_params)
        
        
        req = requests.get(
            'https://www.parsehub.com/api/v2/projects/%s/last_ready_run/data' % #run a project
            self._project_token,
            params=params,
            **(req_params)
        )

        req.raise_for_status()
        return req.text


class PhRun(PhBase):
    def __init__(self, api_key, run_token, **kwargs):
        logging.info('PhRun.__init__(self, api_key="%s", run_token="%s", kwargs="%s").' %
                     (api_key, run_token, dict_except(kwargs, 'jdata')))
        self._run_token = run_token
        super(self.__class__, self).__init__(api_key, **kwargs)
        
    def __repr__(self):
        return '<PhRun(api_key="%s", run_token="%s")>' % (self._api_key, self._run_token)

    def update(self, jdata=None):
        logging.info('PhRun.update(self, jdata="%s").' % ('' if jdata is None else '...'))
        if jdata is None:
            params = self._params
            params['api_key'] = self._api_key
            req_params = self._get_req_params()
        
            logging.debug('PhRun.update: Requesting with params="%s", req_params="%s".' %
                          (params, self._req_params))

            req = requests.get(
                'https://www.parsehub.com/api/v2/runs/%s' % #get a run
                self._run_token,
                params=params,
                **(req_params)
            )
            if req.status_code == 429:
                Warning('Run update limited has been hit -- try sleeping 180s between updates after the first 25 updates for a run...')
            req.raise_for_status()
            jdata = json.loads(req.text)

        self._jdata = jdata
        self._thin = False
    
    def get_data(self, req_params=None, blocking=True, wait_increment=5, wait_timeout=None, connect_timeout=3, download_timeout=600, **kwargs):
        logging.info('PhRun.get_data(self, req_params="%s", blocking="%s", wait_increment=%ss, ' % (req_params, blocking, wait_increment))
        logging.info('\twait_timeout=%ss, connect_timeout=%ss, download_timeout=%ss, ' % (wait_timeout, connect_timeout, download_timeout))
        logging.info('\tkwargs="%s").' % dict_except(kwargs, 'jdata'))
        
        params = kwargs
        params['api_key'] = self._api_key
        req_params = self._get_req_params(req_params, {'timeout': (connect_timeout, download_timeout)})

        logging.debug('PhRun.get_data: Updating run before retrieving data...')
        self.update()

        if not blocking and not self.data_ready:
            raise Exception('Data not ready (non-blocking call).')

        current_wait_time = 0

        while (blocking and not self.data_ready):
            logging.info('PhRun.get_data: Blocking and data not ready, waiting %ss (aggregate: %ss)...' %
                         (wait_increment, current_wait_time))
            time.sleep(wait_increment)
            current_wait_time += wait_increment
            if wait_timeout is not None and current_wait_time >= wait_timeout:
                raise Exception('Timed out waiting for data after %ss.' % current_wait_time)
            logging.debug('PhRun.get_data: Updating data_ready flag...')
            self.update()
        
        logging.debug('PhRun.get_data: Requesting with params="%s", req_params="%s".' % (params, req_params))
        
        req = requests.get(
            'https://www.parsehub.com/api/v2/runs/%s/data' % #get data for a run
            self._run_token,
            params=params,
            **(req_params)
        )

        req.raise_for_status()
        return req.text

    def cancel(self, req_params=None, **kwargs):
        logging.info('PhRun.cancel(self, req_params="%s", kwargs="%s").' % (req_params, dict_except(kwargs, 'jdata')))
        params = kwargs
        params['api_key'] = self._api_key
        req_params = self._get_req_params(req_params)
        
        logging.debug('PhRun.cancel: Requesting with params="%s", req_params="%s".' % (params, req_params))
        
        req = requests.post(
            'https://www.parsehub.com/api/v2/runs/%s/cancel' % #cancel a run
            self._run_token,
            params=params,
            **(req_params)
        )

        req.raise_for_status()
        req_jdata = json.loads(req.text)
        return req_jdata

    def delete(self, req_params=None, **kwargs):
        logging.info('PhRun.delete(self, req_params="%s", kwargs="%s").' % (req_params, dict_except(kwargs, 'jdata')))
        params = kwargs
        params['api_key'] = self._api_key
        req_params = self._get_req_params(req_params)
        
        logging.debug('PhRun.delete: Requesting with params="%s", req_params="%s".' % (params, req_params))
        
        req = requests.delete(
            'https://www.parsehub.com/api/v2/runs/%s' % #delete a run
            self._run_token,
            params=params,
            **(req_params)
        )

        req.raise_for_status()
        req_jdata = json.loads(req.text)
        return req_jdata
