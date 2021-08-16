import requests
import json
from autotoloka_test.create_pool import PoolCreator
from autotoloka_test.create_task import TaskCreator, TaskSuiteCreator
from autotoloka_test.utils import get_chunks
from yadisk import YaDisk


class TolokaProjectHandler:
    """
    Creates a class to handle all Toloka operations
    """

    def __init__(self, ouath_token, project_id=None, sandbox=True, verbose=True, project_params_path=None):
        self.sandbox = sandbox
        self.verbose = verbose
        self.url = 'https://sandbox.toloka.yandex.ru/api/v1/' if sandbox else 'https://toloka.yandex.ru/api/v1/'
        self.oauth_token = ouath_token
        self.headers = {"Authorization": "OAuth " + self.oauth_token}
        if project_id is not None:
            self.project_id = project_id
        else:
            ask_for_project_id = requests.get(self.url + 'projects', headers=self.headers)
            available_proj_ids = [[item['id'],
                                   item['status'],
                                   item['public_name'],
                                   item['created'].split('T')[0]] for item in ask_for_project_id.json()['items']]
            for proj in available_proj_ids:
                if proj[1] != 'ARCHIVED':
                    print(proj)
            flag = True
            while flag:
                input_id = input('Please, type in one of available project IDs (for new project type "NEW"): ')
                if input_id in [item[0] for item in available_proj_ids]:
                    self.project_id = int(input_id)
                    flag = False
                elif input_id.lower() == 'new' and project_params_path is not None:
                    self.project_id = self.create_toloka_project(project_params_path)
                    flag = False

    def print_json(self, item, indent=4):
        """
        Pretty-prints the mutable item
        :param item: mutable item to print
        :param indent: indentation for print
        :return:
        """
        print(json.dumps(item, indent=indent, ensure_ascii=False))

    def create_toloka_project(self, project_params_path='project_params.json'):
        '''
        Creates Toloka project by configuration in a given file
        :param project_params_path: configuration file path
        :return:
        '''
        with open(project_params_path, 'r', encoding='utf-8') as file:
            project_params = json.load(file)
        req = requests.post(self.url + 'projects', headers=self.headers, json=project_params)
        assert req.ok
        new_project_id = req.json()['id']
        if self.verbose:
            self.print_json(req.json())
        print("New project was created. New project id: ", new_project_id)
        output_url = 'https://sandbox.toloka.yandex.ru/requester/project/{}' if self.sandbox \
            else 'https://toloka.yandex.ru/requester/project/{}'
        print(output_url.format(new_project_id))
        return new_project_id

    def update_toloka_project(self, project_params_path=None):
        '''
        Updates the project, obtained by the handler
        :param project_params_path: configuration file path
        :return:
        '''
        if project_params_path is not None:
            with open(project_params_path, 'r', encoding='utf-8') as file:
                self.project_params = json.load(file)
        req = requests.put(self.url + f'projects/{self.project_id}', headers=self.headers, json=self.project_params)
        if req.ok:
            print('The project was successfully updated')

    def get_project_params(self):
        '''
        Prints out project parameters
        :return:
        '''
        req = requests.get(self.url + f'projects/{self.project_id}', headers=self.headers)
        if self.verbose:
            print(req)
        if req.ok:
            self.print_json(req.json())

    def create_toloka_pool(self, pool_from_file=False, file_name=None, **kwargs):
        '''
        Creates Toloka pool by dictionary-stored or file-based configurations
        :param file_name:
        :param pool_from_file: configuration file path
        :param kwargs:
        :return:
        '''
        if pool_from_file:
            with open(file_name, 'r', encoding='utf-8') as file:
                pool_params = json.load(file)
            pool_params['project_id'] = self.project_id
            if 'private_name' in kwargs.keys():
                pool_params['private_name'] = kwargs['private_name']
        else:
            pool_params = PoolCreator(self.project_id, **kwargs).pool
        req = requests.post(self.url + 'pools', headers=self.headers, json=pool_params)
        if self.verbose:
            print(req)
            self.print_json(req.json())
        new_pool_id = req.json()['id']
        print("New pool was created. New pool id: ", new_pool_id)
        output_url = 'https://sandbox.toloka.yandex.ru/requester/pool/{}' if self.sandbox \
            else 'https://toloka.yandex.ru/requester/pool/{}'
        print(output_url.format(new_pool_id))
        if self.project_id is None:
            self.project_id = new_pool_id
        return new_pool_id

    def update_pool(self, pool_id, params_dict):
        '''
        Updates Toloka pool by given parameters
        :param pool_id:
        :param params_dict:
        :return:
        '''
        pool_ids = [int(item[0]) for item in self.get_pools_params()]
        wanted_json = self.get_pools_params(less_info=False)[pool_ids.index(pool_id)]
        for k, v in params_dict.items():
            wanted_json[k] = v
        req = requests.put(self.url + f'pools/{pool_id}', headers=self.headers, json=wanted_json)
        if req.ok:
            print('The project was successfully updated')

    def get_pools_params(self, less_info=True, only_current_project=True):
        '''
        Prints and returns all available pools' parameters
        :param less_info:
        :return:
        '''
        req = requests.get(self.url + 'pools?limit=300&sort=id', headers=self.headers)
        if req.ok:
            output = req.json()['items']
            if less_info:
                to_print = [[f'Pool ID: {item["id"]}',
                             f'Pool status: {item["status"]}',
                             f'Pool name: {item["private_name"]}',
                             f'Project ID: {item["project_id"]}'] for item in output]
                final_print = []
                for item in to_print:
                    if only_current_project:
                        if 'archive' not in item[1].lower() and str(self.project_id) in item[-1]:
                            final_print.append(item)
                    else:
                        if 'archive' not in item[1].lower():
                            final_print.append(item)
                self.print_json(final_print)
                return to_print
            else:
                to_print = []
                for item in output:
                    if only_current_project:
                        if 'archive' not in item['status'].lower() and str(self.project_id) in item['project_id']:
                            to_print.append(item)
                    else:
                        if 'archive' not in item['status'].lower():
                            to_print.append(item)
                self.print_json(to_print)
                return output

    def open_close_pool(self, pool_id, type: str):
        '''
        Opens or closes the required pool
        :param pool_id:
        :param type:
        :return:
        '''
        req_type = 'open' if type.lower() == 'open' else 'close'
        output = requests.post(self.url + f'pools/{pool_id}/{req_type}', headers=self.headers)
        if output.ok:
            print(f'Pool {pool_id} | Operation {req_type.upper()} successfully done')
        try:
            if self.verbose:
                self.print_json(output.json())
        except json.decoder.JSONDecodeError:
            print(f'Most likely, operation {type.upper()} has already been performed')

    def create_task_or_suite(self, pool_id, object='task-suite', input_values=None, tasks_on_suite=10):
        '''
        Creates either a Toloka task or a Toloka task-suite by dictionary-stored input values
        :param pool_id:
        :param object:
        :param input_values:
        :param tasks_on_suite:
        :return:
        '''
        if input_values is not None:
            if len(input_values) <= tasks_on_suite:
                object_creator = TaskCreator(pool_id, input_values).task if object == 'task' else \
                    TaskSuiteCreator(pool_id, input_values).task_suite
            else:
                object_creator = []
                for chunk in get_chunks(input_values, by_length=True, chunk_length=tasks_on_suite):
                    chunk_creator = TaskCreator(pool_id, chunk).task if object == 'task' else \
                        TaskSuiteCreator(pool_id, chunk).task_suite
                    object_creator.append(chunk_creator)
            addition = 'tasks' if object == 'task' else 'task-suites'
            req = requests.post(self.url + f'{addition}?allow_defaults=true', headers=self.headers, json=object_creator)
            if self.verbose:
                print(req)
                self.print_json(req.json())
            if req.ok:
                try:
                    print(f'{object.title()} {req.json()["id"]} successfully created')
                    return req.json()['id']
                except KeyError:
                    print('Task-suites successfully created')

    def create_task_suite_from_yadisk_proxy(self, pool_id, yatoken, proxy_name, object=None, tasks_on_suite=10):
        '''
        Creates either a Toloka task or a Toloka task-suite with data from Ya.Disk proxy-folder
        :param pool_id:
        :param proxy_name:
        :param object:
        :param yatoken:
        :param tasks_on_suite:
        :return:
        '''
        y = YaDisk(token=yatoken)

        selection = [{"data": {"p1": {"x": 0.472, "y": 0.413}, "p2": {"x": 0.932, "y": 0.877}}, "type": "rectangle"},
                     {"data": [{"x": 0.143, "y": 0.807}, {"x": 0.317, "y": 0.87}, {"x": 0.511, "y": 0.145},
                               {"x": 0.328, "y": 0.096}, {"x": 0.096, "y": 0.554}], "type": "polygon"}]

        photos = [file.name for file in list(y.listdir(f'Приложения/Toloka.Sandbox/{proxy_name}'))]
        input_values = [{'image': f'/{proxy_name}/{photo}',
                         'selection': selection
                         } for photo in photos]
        if self.verbose:
            print(f'Photos from {proxy_name} ({len(input_values)} items): ')
            self.print_json(input_values)
        task_id = self.create_task_or_suite(pool_id, object=object, input_values=input_values,
                                            tasks_on_suite=tasks_on_suite)
        return task_id

    def get_toloka_tasks_suites(self, pool_id, object='task-suite'):
        '''
        Prints all available tasks or task-suites in the project
        :param pool_id:
        :return:
        '''
        if object is not None:
            addition = 'tasks' if object == 'task' else 'task-suites'
            req = requests.get(self.url + f'{addition}?pool_id={pool_id}', headers=self.headers)
            print(req)
            if req.ok:
                self.print_json(req.json())
            return req.json()

    def archive_object(self, object_type, object_id):
        '''
        Archives the given object by its ID and type
        :param object_type:
        :param object_id:
        :return:
        '''
        req = requests.post(self.url + f'{object_type}s/{object_id}/archive', headers=self.headers)
        if self.verbose:
            print(req)
            self.print_json(req.json())
        if req.ok:
            print(f'Your object: {object_type}-{object_id} successfully archived')

    def change_task_suite_overlap(self, object_id, overlap=None, object_type=None, infinite_overlap=False):
        '''
        Changes the overlap of either the task or the task-suite, also is able to set infinite overlap
        :param object_id:
        :param overlap:
        :param object_type:
        :param infinite_overlap:
        :return:
        '''
        if object_type is not None:
            addition = 'tasks' if object_type == 'task' else 'task-suites'
            if overlap is not None and infinite_overlap == False:
                js = {'overlap': overlap, 'infinite_overlap': 'false'}
            elif infinite_overlap:
                js = {'overlap': 'null', 'infinite_overlap': 'true'}
            req = requests.patch(self.url + f'{addition}/{object_id}', json=js, headers=self.headers)
            if self.verbose:
                print(req)
                self.print_json(req.json())
            print(f'Overlap in {object_type} successfully changed')

    def stop_showing_task_suite(self, suite_id):
        '''
        Sends the signal to stop showing the task-suite by its ID
        :param suite_id:
        :return:
        '''
        req = requests.patch(self.url + f'task-suites/{suite_id}/set-overlap-or-min', headers=self.headers,
                             json={'overlap': 0})
        if self.verbose:
            print(req)
            self.print_json(req.json())
        if req.ok:
            print(f'Task-suite {suite_id} successfully stopped')

    def get_answers(self, pool_id):
        req = requests.get(self.url + f'assignments?pool_id={pool_id}', headers=self.headers)
        if req.ok:
            if self.verbose:
                print(req)
                self.print_json(req.json())