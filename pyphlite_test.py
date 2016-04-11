from __future__ import print_function
from __future__ import unicode_literals

import hashlib
import logging
import time
import unittest
import warnings
from pyphlite import PhAccount, PhProject, PhRun

DO_END_TO_END_TEST = True #Run an end-to-end test (with data run in the middle)?

warnings.filterwarnings("error")

API_KEY = '<SECRET API KEY>' #REDACTED

static = {
    'project_token': 'tuwGxQIEqV0o3EmKwNqJ8Eav',
    'first_run_token': 'tQ7TZFQMEagc4TLjYDEmohf2',
    'first_run_start_time': '2016-04-11T15:56:03',
    'last_run_token': 'tv75LDrf-CA0G-5orqMe8UTq',
    'data_md5': {
        'json': 'c2420ef00284659f2e125621ba853a6a',
        'csv': 'ac410e709ae74fdcf321ff186a9759f3'
    },
}

dynamic = {
    'project_token': 't2wZQP67r7PCg5Q7q7U3bWda',
    'data_md5': static['data_md5'], #projects are duplicated
}

class Py2and3CompatibleUnitTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Py2and3CompatibleUnitTest, self).__init__(*args, **kwargs)
        
        #Py2-3 hack: assertRaisesRegexp renamed to assertRaisesRegex in Py3 but not yet in Py2
        if not hasattr(self, 'assertRaisesRegex'): 
            self.assertRaisesRegex = self.assertRaisesRegexp

class TestPhAccountStatic(Py2and3CompatibleUnitTest):
    def test_list_projects(self, thin=False):
        acct = PhAccount(API_KEY, thin=thin)
        expected_tokens = sorted([
            static['project_token'],
            dynamic['project_token']
        ])   
        actual_tokens = sorted([
            p.token
            for p in acct.projects
        ])
        self.assertEqual(expected_tokens, actual_tokens)
    
    def test_thin_warning(self):
        with self.assertRaisesRegex(Warning, 'Attempted to access.*'):
            self.test_list_projects(thin=True)

    def test_thin_attribs(self):
        acct = PhAccount(API_KEY, thin=True)

        #Ensure that it's thin
        with self.assertRaises(AttributeError):
            object.__getattribute__(acct, 'projects')

        acct.update()
        
        #Ensure that it's not thin
        self.assertTrue(isinstance(acct.projects[0], PhProject))

def clean_proj_if_necessary(proj):
    proj.update()
    if proj.run_list:
        logging.INFO('Dynamic Test Project started with active runs. Attempting to delete...')
        for run in proj.run_list:
            try:
                run.delete()
            except: pass

    proj.update()
    if proj.run_list:
        raise Exception('Dynamic Test Project started with active runs, and unable to fix.')

class TestPhProjectStatic(Py2and3CompatibleUnitTest):
    def test_get_project(self, thin=False):
        proj = PhProject(API_KEY, static['project_token'], thin=thin)
        expected_runs = sorted([
            static['first_run_token'],
            static['last_run_token']
        ])
        actual_runs = sorted([
            r.run_token
            for r in proj.run_list
        ])
        self.assertEqual(expected_runs, actual_runs)

    def test_thin_warning(self): 
        with self.assertRaisesRegex(Warning, 'Attempted to access.*'):
            self.test_get_project(thin=True)

    def test_thin_attribs(self):
        proj = PhProject(API_KEY, static['project_token'], thin=True)
        
        #Ensure that it's thin
        with self.assertRaises(AttributeError):
            object.__getattribute__(proj, 'run_list')

        proj.update()
        
        #Ensure that it's not thin
        self.assertTrue(isinstance(proj.run_list[0], PhRun))

    def test_get_last_data(self, output_format=None):
        proj = PhProject(API_KEY, static['project_token'])
        if output_format is None:
            data = proj.get_last_ready_data()
            expected_hash = static['data_md5']['json'] #default is json
        else:
            data = proj.get_last_ready_data(format=output_format)
            expected_hash = static['data_md5'][output_format]

        actual_hash = hashlib.md5(data.encode('utf-8')).hexdigest()
        self.assertEqual(actual_hash, expected_hash)

    def test_get_last_data_json(self):
        self.test_get_last_data(output_format='json')

    def test_get_last_data_csv(self):
        self.test_get_last_data(output_format='csv')

class TestPhProjectDynamic(Py2and3CompatibleUnitTest):
    def test_run_project(self):
        proj = PhProject(API_KEY, dynamic['project_token']) #DYNAMIC!!

        clean_proj_if_necessary(proj)

        initial_run_tokens = sorted([r.run_token for r in proj.run_list])
        
        new_run = proj.run()
        proj.update()
        current_run_tokens = sorted([r.run_token for r in proj.run_list])

        new_tokens = sorted(set(initial_run_tokens) | set(current_run_tokens))
        self.assertEqual(len(new_tokens),1)
        self.assertEqual(new_tokens[0], new_run.run_token)

        try:
            new_run.delete()
        except:
            pass

class TestPhRunStatic(Py2and3CompatibleUnitTest):

    #Significant modifications were necessary due to rate limiting
    # - Run update limits are: first 25 updates anytime, 180s per update after that
    # - So, combine everything into one test that only updates once:

    def test_thin_load_once(self):
        run = PhRun(API_KEY, static['first_run_token'], thin=True)

        #Ensure that it's thin
        with self.assertRaises(AttributeError):
            object.__getattribute__(self, 'status')

        #Try to access an item; make sure that it raises an warning
        with self.assertRaisesRegex(Warning, 'Attempted to access.*'):
            run.status
            
        #Ensure that we can update it and get into
        run.update()
        self.assertEqual(run.status, "complete")

        #Check that it has the expected start time
        self.assertEqual(run.start_time, static['first_run_start_time'])

''' 
    def test_get_run(self, thin=False):
        run = PhRun(API_KEY, static['first_run_token'], thin=thin)
        self.assertEqual(run.start_time, static['first_run_start_time'])

    def test_thin_warning(self):
        if not hasattr(self, 'assertRaisesRegex'): #Py2-3 hack (renamed)
            self.assertRaisesRegex = self.assertRaisesRegexp

        with self.assertRaisesRegex(Warning, 'Attempted to access.*'):
            self.test_get_run(thin=True)

    def test_thin_attribs(self):
        run = PhRun(API_KEY, static['first_run_token'], thin=True)
        self.assertFalse(hasattr(run, 'status'))
        run.update()
        self.assertTrue(hasattr(run, 'status'))

    def test_get_data(self, output_format=None):
        run = PhRun(API_KEY, static['first_run_token'], thin=True)
        
        if output_format is None:
            data = run.get_data(wait_increment=20)
            expected_hash = static['data_md5']['json'] #default is json
        else:
            data = run.get_data(wait_increment=20, format=output_format)
            expected_hash = static['data_md5'][output_format]
            
        actual_hash = hashlib.md5(data).hexdigest()
        self.assertEqual(actual_hash, expected_hash)

    def test_get_data_json(self):
        self.test_get_data(output_format='json')

    def test_get_data_csv(self):
        self.test_get_data(output_format='csv')

'''

class TestPhRunDynamic(Py2and3CompatibleUnitTest):
    def setUp(self):
        self.proj = PhProject(API_KEY, dynamic['project_token'], thin=True) #DYNAMIC!!
        clean_proj_if_necessary(self.proj)

    def tearDown(self): #delete everything... if you can
        try:
            proj.update()
        except: pass

        try:
            for run in proj.run_list:
                try:
                    run.delete()
                except: pass
        except:
            pass
    
    def test_cancel(self):
        initial_run_tokens = sorted([r.run_token for r in self.proj.run_list])
        new_run = self.proj.run()
        self.proj.update()
        current_run_tokens = sorted([r.run_token for r in self.proj.run_list])
        self.assertEqual(len(current_run_tokens), 1)
        self.assertEqual(current_run_tokens[0], new_run.run_token)

        new_run.cancel()
        new_run.update()
        self.assertEqual(new_run.status, 'cancelled')

        try:
            new_run.delete()
        except: pass

    def test_delete(self):
        initial_run_tokens = sorted([r.run_token for r in self.proj.run_list])
        new_run = self.proj.run()
        self.proj.update()
        current_run_tokens = sorted([r.run_token for r in self.proj.run_list])
        self.assertEqual(len(current_run_tokens), 1)
        self.assertEqual(current_run_tokens[0], new_run.run_token)

        new_run.delete()

        self.proj.update()
        final_run_tokens = sorted([r.run_token for r in self.proj.run_list])
        self.assertEqual(len(final_run_tokens), 0)

    def test_end_to_end_with_formats(self):
        if not DO_END_TO_END_TEST:
            raise Warning('DO_END_TO_END_TEST = False, skipping...')
        
        new_run = self.proj.run()
        self.proj.update()
        self.assertEqual(len(self.proj.run_list), 1)
        self.assertEqual(self.proj.run_list[0].run_token, new_run.run_token)

    
        default_data = new_run.get_data(wait_increment=30)
        default_hash = hashlib.md5(default_data.encode('utf-8')).hexdigest()
        self.assertEqual(default_hash, dynamic['data_md5']['json']) #default is json

        json_data = new_run.get_data(wait_timeout=5, format='json')
        json_hash = hashlib.md5(json_data.encode('utf-8')).hexdigest()
        self.assertEqual(json_hash, dynamic['data_md5']['json'])

        csv_data = new_run.get_data(wait_timeout=5, format='csv')
        csv_hash = hashlib.md5(csv_data.encode('utf-8')).hexdigest()
        self.assertEqual(csv_hash, dynamic['data_md5']['csv'])

        new_run.delete()
        self.proj.update()
        self.assertEqual(len(self.proj.run_list), 0)
        
if __name__ == '__main__':
    unittest.main()
