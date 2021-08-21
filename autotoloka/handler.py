import requests
import json
import os
import time
from autotoloka.create_pool import PoolCreator
from autotoloka.create_task import TaskSuiteCreator
from autotoloka.utils import get_chunks
from yadisk import YaDisk
from autotoloka.json_data import json_data, path
from sys import stdout


class TolokaProjectHandler:
    """
    Creates a class to handle all Toloka operations
    """

    def __init__(self, ouath_token, project_id=None, is_sandbox=True, verbose=True, project_params_data=None):
        """
        Instantiates a TolokaProjectHandler class

        :param ouath_token: Yandex.Toloka token for connecting with the API
        :param project_id: ID of the project the handler is needed for, if None - various options will be given
        :param is_sandbox: if set to True, then all the operations will be performed in Sandbox Toloka
        :param verbose: if set to True, all response logs will be printed out
        :param project_params_data: a json-like dictionary of project configurations, needed for creating new project
        """
        self.sandbox = is_sandbox
        self.verbose = verbose
        self.url = 'https://sandbox.toloka.yandex.ru/api/v1/' if is_sandbox else 'https://toloka.yandex.ru/api/v1/'
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
                elif input_id.lower() == 'new' and project_params_data is not None:
                    self.project_id = self.create_toloka_project(project_params_data)
                    flag = False

    def print_json(self, item, indent=4):
        """
        Pretty-prints the mutable item

        :param item: mutable item to print
        :param indent: indentation for print
        """
        print(json.dumps(item, indent=indent, ensure_ascii=False))

    def create_toloka_project(self, project_params_data=json_data['validating_segmentation']):
        """
        Creates Toloka project by configuration in a given json-like data

        :param project_params_data: a json-like dictionary of project configurations
        :return: ID of a new project
        """
        response = requests.post(self.url + 'projects', headers=self.headers, json=project_params_data)
        assert response.ok
        new_project_id = response.json()['id']
        if self.verbose:
            self.print_json(response.json())
        print("New project was created. New project id: ", new_project_id)
        output_url = 'https://sandbox.toloka.yandex.ru/requester/project/{}' if self.sandbox \
            else 'https://toloka.yandex.ru/requester/project/{}'
        print(output_url.format(new_project_id))
        return new_project_id

    def update_toloka_project(self, project_params_data=None):
        """
        Updates the project, obtained by the handler

        :param project_params_data: a json-like dictionary of project configurations
        """
        if project_params_data is not None:
            response = requests.put(self.url + f'projects/{self.project_id}', headers=self.headers,
                                    json=project_params_data)
            if response.ok:
                print('The project was successfully updated')

    def get_project_params(self):
        """
        Prints out project parameters

        :return: response of the GET-request in a json-like structure
        """
        response = requests.get(self.url + f'projects/{self.project_id}', headers=self.headers)
        if self.verbose:
            print(response)
        if response.ok:
            self.print_json(response.json())
        return response.json()

    def create_toloka_pool(self, pool_from_json_data=None, **kwargs):
        """
        Creates Toloka pool by dictionary-stored or file-based configurations

        :param pool_from_json_data: a json-like dictionary of pool configurations
        :param kwargs: keyword arguments for PoolCreator class instance
        :return: ID of a new pool
        """
        if pool_from_json_data:
            pool_params = pool_from_json_data
            pool_params['project_id'] = self.project_id
            if 'private_name' in kwargs.keys():
                pool_params['private_name'] = kwargs['private_name']
        else:
            pool_params = PoolCreator(self.project_id, **kwargs).pool
        response = requests.post(self.url + 'pools', headers=self.headers, json=pool_params)
        if self.verbose:
            print(response)
            self.print_json(response.json())
        new_pool_id = response.json()['id']
        print("New pool was created. New pool id: ", new_pool_id)
        output_url = 'https://sandbox.toloka.yandex.ru/requester/pool/{}' if self.sandbox \
            else 'https://toloka.yandex.ru/requester/pool/{}'
        print(output_url.format(new_pool_id))
        if self.project_id is None:
            self.project_id = new_pool_id
        return new_pool_id

    def update_pool(self, pool_id, pool_from_json_data):
        """
        Updates Toloka pool by given parameters

        :param pool_id: ID of a Toloka pool
        :param pool_from_json_data: a json-like dictionary of pool configurations
        """
        pool_ids = [int(item[0]) for item in self.get_pools_params()]
        wanted_json = self.get_pools_params(less_info=False)[pool_ids.index(pool_id)]
        for k, v in pool_from_json_data.items():
            wanted_json[k] = v
        response = requests.put(self.url + f'pools/{pool_id}', headers=self.headers, json=wanted_json)
        if response.ok:
            print('The project was successfully updated')

    def get_pools_params(self, pool_id=None, less_info=True, only_current_project=True):
        """
        Prints and returns either all available pools' parameters or certain pool's parameters (by its ID)

        :param pool_id: ID of the pool, if set than only given pool's parameters are printed and returned
        :param less_info: if set to True, method prints out only pool's ID, status, name and creation date,
                            otherwise method prints all the pool parameters
        :param only_current_project: if set to True, prints out only pools from the current project
        :return: information for printing
        """
        if pool_id is not None:
            response = requests.get(self.url + f'pools/{pool_id}', headers=self.headers)
            if self.verbose:
                self.print_json(response.json())
            return response.json()
        else:
            response = requests.get(self.url + 'pools?limit=300&sort=id', headers=self.headers)
            if response.ok:
                output = response.json()['items']
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
                    return final_print
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
                    return to_print

    def open_close_pool(self, pool_id):
        """
        Opens or closes the required pool

        :param pool_id: ID of the pool
        """
        pool_params = requests.get(self.url + f'pools/{pool_id}', headers=self.headers).json()
        status, reason = pool_params['status'], pool_params.get('last_close_reason')
        req_type = 'open' if status == 'CLOSED' else 'close'
        if reason == 'COMPLETED':
            print(f'The pool-{pool_id} has already been closed due to completion')
            return None
        response = requests.post(self.url + f'pools/{pool_id}/{req_type}', headers=self.headers)
        if response.ok:
            print(f'Pool {pool_id} | Operation {req_type.upper()} successfully done')
        try:
            if self.verbose:
                self.print_json(response.json())
        except json.decoder.JSONDecodeError:
            print(f'Most likely, operation {req_type.upper()} has already been performed')

    def create_task_suite(self, pool_id, input_values=None, tasks_on_suite=10):
        """
        Creates either a Toloka task or a Toloka task-suite by dictionary-stored input values

        :param pool_id: ID of the pool
        :param input_values: a list of dictionaries with a certain key-value structure,
                            check get_project_params method for reference
        :param tasks_on_suite: the number of tasks on one suite
        :return: ID of a new task-suite
        """
        if input_values is not None:
            if len(input_values) <= tasks_on_suite:
                object_creator = TaskSuiteCreator(pool_id, input_values).task_suite
            else:
                object_creator = []
                for chunk in get_chunks(input_values, by_length=True, chunk_length=tasks_on_suite):
                    chunk_creator = TaskSuiteCreator(pool_id, chunk).task_suite
                    object_creator.append(chunk_creator)
            response = requests.post(self.url + f'task-suites?allow_defaults=true', headers=self.headers,
                                     json=object_creator)
            if self.verbose:
                print(response)
                self.print_json(response.json())
            if response.ok:
                try:
                    print(f'Task-suite {response.json()["id"]} successfully created')
                    return response.json()['id']
                except KeyError:
                    print('Task-suites successfully created')

    def create_task_suite_from_yadisk_proxy(self, pool_id, yatoken, proxy_name, tasks_on_suite=10):
        """
        Creates either a Toloka task or a Toloka task-suite with data from Ya.Disk proxy-folder

        :param pool_id: ID of the pool
        :param proxy_name: name of proxy defined in Toloka Options
        :param yatoken: yadisk token needed for connecting with Yandex.Disk API
        :param tasks_on_suite: the number of tasks on one suite
        :return: ID of a new task-suite
        """
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
        task_id = self.create_task_suite(pool_id, input_values=input_values, tasks_on_suite=tasks_on_suite)
        return task_id

    def get_toloka_tasks_suites(self, pool_id):
        """
        Prints all available tasks or task-suites in the project

        :param pool_id: ID of the pool
        :return: a JSON response of GET request, containing task-suites' data
        """
        response = requests.get(self.url + f'task-suites?pool_id={pool_id}', headers=self.headers)
        print(response)
        if response.ok:
            self.print_json(response.json())
        return response.json()

    def archive_object(self, object_type, object_id):
        """
        Archives the given object by its ID and type

        :param object_type: 'project', 'pool' or 'task-suite'
        :param object_id: ID of the object
        """
        response = requests.post(self.url + f'{object_type}s/{object_id}/archive', headers=self.headers)
        if self.verbose:
            print(response)
            self.print_json(response.json())
        if response.ok:
            print(f'Your object: {object_type}-{object_id} successfully archived')

    def change_task_suite_overlap(self, task_suite_id, overlap=None, infinite_overlap=False):
        """
        Changes the overlap of either the task or the task-suite, also is able to set infinite overlap

        :param task_suite_id: ID of the task-suite
        :param overlap: overlap value
        :param infinite_overlap: if set to True, sets the value to infinite overlap
        """
        if overlap is not None and infinite_overlap is False:
            js = {'overlap': overlap, 'infinite_overlap': 'false'}
        elif infinite_overlap:
            js = {'overlap': 'null', 'infinite_overlap': 'true'}
        response = requests.patch(self.url + f'task-suites/{task_suite_id}', json=js, headers=self.headers)
        if self.verbose:
            print(response)
            self.print_json(response.json())
        print(f'Overlap in task-suite {task_suite_id} successfully changed')

    def stop_showing_task_suite(self, task_suite_id):
        """
        Sends the signal to stop showing the task-suite by its ID

        :param task_suite_id: ID of the task-suite
        """
        response = requests.patch(self.url + f'task-suites/{task_suite_id}/set-overlap-or-min', headers=self.headers,
                             json={'overlap': 0})
        if self.verbose:
            print(response)
            self.print_json(response.json())
        if response.ok:
            print(f'Task-suite {task_suite_id} successfully stopped')

    def get_answers(self, pool_id):
        """
        Prints out all the answers of the given pool

        :param pool_id: ID of the pool
        :return: a json-like response
        """
        response = requests.get(self.url + f'assignments?pool_id={pool_id}', headers=self.headers)
        if response.ok:
            if self.verbose:
                print(response)
                self.print_json(response.json())
            return response.json()

    def get_files_from_pool(self, pool_id, download_folder_name):
        """
        Downloads all the files from the pool into a folder

        :param pool_id: ID of the pool
        :param download_folder_name: name of a directory to download all the files into
        """
        response = requests.get(self.url + f'attachments?pool_id={pool_id}&limit=100', headers=self.headers)
        if response.ok:
            if self.verbose:
                print(response)
                self.print_json(response.json())
            file_ids = (item['id'] for item in response.json()['items'])
            file_names = [item['name'] for item in response.json()['items']]
            unique_file_names = {}

            # Making sure that there will be no files with identical names
            for i, file_name in enumerate(file_names):
                if file_name[:-4] not in unique_file_names.keys():
                    unique_file_names[file_name[:-4]] = 1
                else:
                    file_names[i] = f'{file_name[:-4]}_{unique_file_names[file_name[:-4]] + 1}.jpg'
                    unique_file_names[file_name[:-4]] += 1

            download_path = os.path.join(os.getcwd(), download_folder_name)

            if download_folder_name not in os.listdir(os.getcwd()):
                os.mkdir(download_folder_name)
                print(f'Directory {download_folder_name} created')

            print('Downloading files ... ')
            for i, id in enumerate(file_ids):
                download = requests.get(self.url + f'attachments/{id}/download', headers=self.headers)
                with open(os.path.join(download_path, file_names[i]), 'wb') as file:
                    file.write(download.content)

            print(f'All files from pool-{pool_id} successfully downloaded into {download_path}')

    def accept_all_tasks(self, pool_id):
        """
        Accepts all the assignments in a given pool

        :param pool_id: ID of the pool
        """
        assignments = requests.get(self.url + f'assignments?pool_id={pool_id}', headers=self.headers).json()
        assignment_ids = [item['id'] for item in assignments['items']]
        for id in assignment_ids:
            patch_params = {'status': 'ACCEPTED', 'public_comment': 'Well done, dude!'}
            response = requests.patch(self.url + f'assignments/{id}', headers=self.headers, json=patch_params)
            if response.ok:
                print(f'Assignment {id} successfully accepted')
            else:
                if self.verbose:
                    self.print_json(response.json())

    @staticmethod
    def write_config_to_json_files(config_data: dict, file_name: str):
        """
        Writes the json-like configuration data into a file and stores it in json_files directory

        :param config_data: a json-like dictionary
        :param file_name: a name of a file to store the configurations in
        """
        if file_name is None or file_name[-5:] == '.json':
            raise ValueError('Please, provide the file_name without specifying the format')
        with open(f'{path}/{file_name}.json', 'w') as file:
            json.dump(config_data, file, indent=4)


if __name__ == '__main__':
    token = 'AQAAAABVFx8TAAIbupmTNSLnLE9ostJWyUWHY-M'
    collect_photos_config = json_data['collecting_images']
    collect_photos_config['public_name'] = "Let's collect some photos!!"
    # project_id, pool_id = 74564, 960803
    # handler = TolokaProjectHandler(token, project_id=project_id)
    handler = TolokaProjectHandler(token, verbose=False, project_params_data=collect_photos_config)
    project_id = handler.project_id

    pool_id = handler.create_toloka_pool(private_name='Test_Name')
    input_values = [
        {'product_title': 'title_1'},
        {'product_title': 'title_2'},
        {'product_title': 'title_3'},
        {'product_title': 'title_4'},
        {'product_title': 'title_5'}
    ]
    handler.create_task_suite(pool_id, input_values, tasks_on_suite=1)
    closed = handler.get_pools_params(pool_id).get('last_close_reason')
    handler.open_close_pool(pool_id)

    # Progress bar parameters
    bar, bar_length = '█', 50
    bar_step = int(bar_length / len(input_values))

    while closed != 'COMPLETED':
        time.sleep(5)
        closed = handler.get_pools_params(pool_id).get('last_close_reason')
        active_tasks = handler.get_answers(pool_id)['items']
        statuses = [task['status'] for task in active_tasks]
        counter = statuses.count('SUBMITTED') if statuses else 0
        stdout.write('\rPhotos uploaded: {}/{} |{}{}|'.format(counter, len(input_values),
                                                              bar * bar_step * counter,
                                                              '-' * bar_step * (len(input_values) - counter)))
        stdout.flush()
    print('')
    handler.get_files_from_pool(pool_id, 'photos')
    # handler.open_close_pool(pool_id)
    handler.accept_all_tasks(pool_id)
    handler.archive_object('pool', pool_id)
    handler.archive_object('project', project_id)
