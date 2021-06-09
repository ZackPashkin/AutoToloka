import requests
import json
from src.pool_creator import PoolCreator
from src.task_creator import TaskCreator, TaskSuiteCreator


class TolokaProjectHandler:
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
            available_proj_ids = [[item['id'], item['status']] for item in ask_for_project_id.json()['items']]
            print(*available_proj_ids, sep='\n')
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
        print(json.dumps(item, indent=indent, ensure_ascii=False))

    def create_toloka_project(self, project_params_path='project_params.json'):
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
        if project_params_path is not None:
            with open(project_params_path, 'r', encoding='utf-8') as file:
                self.project_params = json.load(file)
        req = requests.put(self.url + f'projects/{self.project_id}', headers=self.headers, json=self.project_params)
        if req.ok:
            print('The project was successfully updated')

    def update_pool(self, pool_id, params_dict):
        pool_ids = [int(item[0]) for item in self.get_pools_params()]
        wanted_json = self.get_pools_params(less_info=False)[pool_ids.index(pool_id)]
        for k, v in params_dict.items():
            wanted_json[k] = v
        req = requests.put(self.url + f'pools/{pool_id}', headers=self.headers, json=wanted_json)
        if req.ok:
            print('The project was successfully updated')

    def create_toloka_pool(self, pool_from_file=False, **kwargs):
        if pool_from_file:
            with open('pool_params.json', 'r', encoding='utf-8') as file:
                pool_params = json.load(file)
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

    def get_pools_params(self, less_info=True):
        req = requests.get(self.url + 'pools', headers=self.headers)
        if req.ok:
            output = req.json()['items']
            if less_info:
                to_print = [[f'Pool ID: {item["id"]}',
                         f'Pool status: {item["status"]}',
                         f'Pool name: {item["private_name"]}',
                         f'Project ID: {item["project_id"]}'] for item in output]
                self.print_json(to_print)
                return to_print
            else:
                self.print_json(output)
                return output

    def get_project_params(self):
        req = requests.get(self.url + f'projects/{self.project_id}', headers=self.headers)
        if req.ok:
            self.print_json(req.json())

    def open_close_pool(self, pool_id, type: str):
        req_type = 'open' if type.lower() == 'open' else 'close'
        output = requests.post(self.url + f'pools{pool_id}/{req_type}', headers=self.headers)
        if output.ok:
            print(f'Pool {pool_id} | Operation {req_type.upper()} successfully done')
        try:
            if self.verbose:
                self.print_json(output.json())
        except json.decoder.JSONDecodeError:
            print(f'Most likely, operation {type.upper()} has already been performed')

    def archive_object(self, object_type, object_id):
        req = requests.post(self.url + f'{object_type}s/{object_id}/archive', headers=self.headers)
        if self.verbose:
            print(req)
            self.print_json(req.json())
        if req.ok:
            print(f'Your object: {object_type}-{object_id} successfully archived')

    def get_toloka_tasks(self, pool_id):
        req = requests.get(self.url + f'tasks?pool_id={pool_id}', headers=self.headers)
        print(req)
        if req.ok:
            self.print_json(req.json())

    def get_toloka_task_suites(self, pool_id):
        req = requests.get(self.url + f'task-suites?pool_id={pool_id}', headers=self.headers)
        print(req)
        if req.ok:
            self.print_json(req.json())

    def create_task_or_suite(self, pool_id, object=None, input_values=None):
        if input_values is not None:
            object = TaskCreator(pool_id, input_values).task if object == 'task' else \
                TaskSuiteCreator(pool_id, input_values).task_suite
            addition = 'tasks' if object == 'task' else 'task-suites'
            req = requests.post(self.url + f'{addition}?allow_defaults=true', headers=self.headers, json=object)
            if req.ok:
                return req.json()['id']

    def change_object_overlap(self, object_id, overlap=None, object_type=None, infinite_overlap=False):
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
        pass


# Greg Project: 64894

if __name__ == '__main__':
    Greg, Arina = 'AQAAAABVFx8TAAIbuv-O6f5F5UdQpaujoE7VnNk', 'AQAAAAAOLepkAAIbukKmFBAvCkpluhXdXMFEyzo'
    handler = TolokaProjectHandler(Greg, project_id=66187)
    # handler.update_toloka_project('project_params_2.json')
    # handler.get_project_params()
    # project = handler.create_toloka_project()
    # handler.archive_object('project', 66187)
    # handler.update_toloka_project(64894)
    # pool = handler.create_toloka_pool()
    # handler.open_close_pool(handler.get_pools_params(), 'close')
    # handler.create_toloka_pool(pool_from_file=False, private_name='Test Pool 1')
    handler.get_pools_params(less_info=False)
    # handler.get_toloka_task_suites(900589)
    input_values = [{'image': 'https://crosti.ru/patterns/00/12/02/4835fab2d8/picture.jpg'},
                    {'image': 'https://vignette.wikia.nocookie.net/calicoswarriorsrp/images/0/05/Stumpyboy.jpg/revision/latest?cb=20181217042736'},
                    {'image': 'https://i.pinimg.com/736x/09/04/b2/0904b2000fa6b0982167e799e91e4e08.jpg'}]
    # handler.create_task_or_suite(900352, 'task-suite', input_values)
    # handler.change_object_overlap('00000dbd00--60c01f5ae7a2eb796ef5002b', 1, 'task-suite')