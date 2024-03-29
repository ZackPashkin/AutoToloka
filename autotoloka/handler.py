import requests
import json
import os
from tqdm import tqdm
from autotoloka.create_pool import PoolCreator
from autotoloka.create_task import TaskSuiteCreator
from autotoloka.utils import get_chunks, print_json, check_for_duplicates
from yadisk import YaDisk
from autotoloka.json_data import json_data


class TolokaProjectHandler:
    """
    Creates a class to handle all Toloka operations
    """
    def __init__(self, oauth_token=None, project_id=None, is_sandbox=True, verbose=True, project_params_data=None):
        """
        Instantiates a TolokaProjectHandler class

        :param oauth_token: Yandex.Toloka token for connecting with the API
        :param project_id: ID of the project the handler is needed for, if None - various options will be given
        :param is_sandbox: if set to True, then all the operations will be performed in Sandbox Toloka
        :param verbose: if set to True, all response logs will be printed out
        :param project_params_data: a json-like dictionary of project configurations, needed for creating new project
        """
        self.sandbox = is_sandbox
        self.verbose = verbose
        self.url = 'https://sandbox.toloka.yandex.ru/api/v1/' if is_sandbox else 'https://toloka.yandex.ru/api/v1/'

        if oauth_token is None:
            input_oauth = input('Please, type in your Yandex.Toloka token: ')
            self.oauth_token = input_oauth
        else:
            self.oauth_token = oauth_token
        self.headers = {"Authorization": "OAuth " + self.oauth_token}

        if project_id is not None:
            self.project_id = project_id
        else:
            ask_for_project_id = requests.get(self.url + 'projects?limit=300', headers=self.headers)
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
            print_json(response.json())
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
            print_json(response.json())
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
            print_json(response.json())
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
                print_json(response.json())
            return response.json()
        else:
            if only_current_project:
                response = requests.get(self.url + f'pools?limit=300&sort=id&project_id={self.project_id}',
                                        headers=self.headers)
            else:
                response = requests.get(self.url + 'pools?limit=300&sort=id', headers=self.headers)
            if response.ok:
                output = response.json()['items']
                if less_info:
                    to_print = [{'Pool ID': item["id"],
                                 'Pool status': item["status"],
                                 'Pool name': item["private_name"],
                                 'Project ID': item["project_id"]} for item in output]
                    final_print = []
                    for item in to_print:
                        if 'archive' not in item['Pool status'].lower():
                            final_print.append(item)
                    print_json(final_print)
                    return final_print
                else:
                    to_print = []
                    for item in output:
                        if 'archive' not in item['status'].lower():
                            to_print.append(item)
                    print_json(to_print)
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
                print_json(response.json())
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
                print_json(response.json())
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
            print_json(input_values)
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
            print_json(response.json())
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
            print_json(response.json())
        if response.ok:
            print(f'Your object: {object_type}-{object_id} successfully archived')
        elif response.status_code == 409:
            if response.json()['code'] == 'UNARCHIVED_POOLS_CONFLICT':
                pools = self.get_pools_params()
                for pool in pools:
                    if pool['Pool status'] == 'OPEN':
                        self.open_close_pool(pool['Pool ID'])
                    self.process_all_tasks(pool['Pool ID'], action='accept')
                    self.archive_object('pool', pool['Pool ID'])
                self.archive_object(object_type, object_id)
            elif response.json()['code'] == 'SUBMITTED_ASSIGNMENTS_CONFLICT':
                self.process_all_tasks(object_id, 'accept')
                self.archive_object(object_type, object_id)
            elif response.json()['code'] == 'THERE_IS_REJECTED_ASSIGNMENT':
                self.process_all_tasks(object_id, 'accept')
                self.archive_object(object_type, object_id)

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
            print_json(response.json())
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
            print_json(response.json())
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
                print_json(response.json())
            return response.json()

    def get_files_from_pool(self, pool_id, download_folder_name, reject_errors=False):
        """
        Downloads all the files from the pool into a folder

        :param reject_errors: reject the task if no photo was uploaded
        :param pool_id: ID of the pool
        :param download_folder_name: name of a directory to download all the files into
        :return: photo data dictionary {assignment ID: {image ID: str, image name: str, is duplicate: bool}}
        """
        response = requests.get(self.url + f'assignments?pool_id={pool_id}&limit=100', headers=self.headers)
        if response.ok:
            if self.verbose:
                print(response)
                print_json(response.json())
            photo_data = {}
            assignments = response.json()['items']
            for assignment in assignments:
                output_values = assignment['solutions'][0]['output_values']
                if output_values['no_image']:
                    photo_data[assignment['id']] = None
                else:
                    photo_data[assignment['id']] = {'image_id': output_values['image'],
                                                    'image_name': None,
                                                    'is_duplicate': False}

            for key in photo_data:
                if photo_data.get(key) is None:
                    if reject_errors:
                        self.process_task(key, 'reject', 'no photo uploaded')
                else:
                    image_response = requests.get(self.url + f'attachments/{photo_data[key]["image_id"]}',
                                                  headers=self.headers)
                    photo_data[key]['image_name'] = image_response.json()['name']

            unique_file_names = {}

            # Making sure that there will be no files with identical names
            for key in photo_data:
                if photo_data[key] is not None:
                    file_name = photo_data[key]['image_name']
                    if file_name[:-4] not in unique_file_names.keys():
                        unique_file_names[file_name[:-4]] = 1
                    else:
                        new_file_name = f'{file_name[:-4]}_{unique_file_names[file_name[:-4]] + 1}.jpg'
                        photo_data[key]['image_name'] = new_file_name
                        unique_file_names[file_name[:-4]] += 1

            download_path = os.path.join(os.getcwd(), download_folder_name)

            if download_folder_name not in os.listdir(os.getcwd()):
                os.mkdir(download_folder_name)
                print(f'Directory {download_folder_name} created')

            print('Downloading files ... ')

            for key in tqdm(photo_data, ncols=100, colour='green', desc='Photo data processed'):
                if photo_data[key] is not None:
                    file_id = photo_data[key]['image_id']
                    download = requests.get(self.url + f'attachments/{file_id}/download', headers=self.headers)
                    with open(os.path.join(download_path, photo_data[key]["image_name"]), 'wb') as file:
                        file.write(download.content)


            print(f'All files from pool-{pool_id} successfully downloaded into {download_path}')
            if self.verbose:
                print_json(photo_data)
            return photo_data

    def process_all_tasks(self, pool_id, action='accept'):
        """
        Processes all the assignments in a given pool, accepting or rejecting them

        :param action: either 'accept' or 'reject'
        :param pool_id: ID of the pool
        """
        assignments = requests.get(self.url + f'assignments?pool_id={pool_id}', headers=self.headers).json()
        assignment_ids = [item['id'] for item in assignments['items']]
        assignment_statuses = [item['status'] for item in assignments['items']]
        for i, assignment_id in enumerate(assignment_ids):
            if assignment_statuses[i] == 'SUBMITTED':
                self.process_task(assignment_id, action)
            else:
                if assignment_statuses[i] == 'REJECTED' and action == 'accept':
                    self.process_task(assignment_id, action)

    def process_task(self, assignment_id, action='accept', public_comment='generic comment'):
        """
        Processes the assignment by its ID, accepting or rejecting it

        :param public_comment: public comment for the user whose task is accepted/rejected
        :param action: either 'accept' or 'reject'
        :param assignment_id: ID of the assignment
        """
        assignment_options = {'accept': {'status': 'ACCEPTED',
                                         'public_comment': public_comment},
                              'reject': {'status': 'REJECTED',
                                         'public_comment': public_comment}}
        patch_params = assignment_options[action]
        response = requests.patch(self.url + f'assignments/{assignment_id}', headers=self.headers, json=patch_params)
        if response.ok:
            print(f'Assignment {assignment_id} successfully {action}ed with public comment: {public_comment}')
        elif response.status_code == 409 and response.json()['code'] == 'INAPPROPRIATE_STATUS':
            print(f'Probably, the assignment {assignment_id} has already been {action}ed')
        else:
            if self.verbose:
                print(response)
                print_json(response.json())

    def check_photos_for_duplicates(self, image_folder, reject_duplicates=False,
                                    accept_uniques=False, photo_data=None):
        """
        Checks uploaded photos for duplicates and processes tasks based on the CNN results

        :param image_folder: folder where uploaded images are stored
        :param reject_duplicates: if set to True, rejects tasks where duplicates were provided
        :param accept_uniques: if set to True, accepts tasks with uniques
        :param photo_data: photo data dictionary from get_files_from_pool function
        """
        print('Checking for duplicates ...')
        images_to_reject = check_for_duplicates(image_folder)
        if self.verbose:
            print_json(images_to_reject)
        for key in photo_data:
            if photo_data[key] is not None:
                if photo_data[key]['image_name'] in images_to_reject:
                    if reject_duplicates:
                        photo_data[key]['is_duplicate'] = True
                        comment = "It seems that this image's duplicate has already been provided by someone else"
                        self.process_task(key, action='reject', public_comment=comment)
                else:
                    if accept_uniques:
                        self.process_task(key, 'accept', 'Well done!')
            if self.verbose:
                print_json(photo_data)


if __name__ == '__main__':
    token = 'AQAAAABVFx8TAAIbupmTNSLnLE9ostJWyUWHY-M'
