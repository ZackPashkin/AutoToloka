import requests
import time
import numpy as np
import pandas as pd
import json
from pool_creator import PoolCreator


class TolokaProjectHandler:
    def __init__(self, ouath_token, project_id=None, sandbox=True):
        self.url = 'https://sandbox.toloka.yandex.ru/api/v1/' if sandbox else 'https://toloka.yandex.ru/api/v1/'
        self.oauth_token = ouath_token
        self.headers = {"Authorization": "OAuth " + self.oauth_token}
        with open('project_params.json', 'r', encoding='utf-8') as file:
            self.project_params = json.load(file)
        # with open('pool_params.json', 'r', encoding='utf-8') as file:
        #     self.pool_params = json.load(file)
        if project_id is not None:
            self.project_id = project_id
        else:
            ask_for_project_id = requests.get(self.url + 'projects', headers=self.headers)
            available_proj_ids = [[item['id'], item['status']] for item in ask_for_project_id.json()['items']]
            print(*available_proj_ids, sep='\n')
            flag = True
            while flag:
                input_id = input('Please, type in one of available project IDs: ')
                if input_id in [item[0] for item in available_proj_ids]:
                    self.project_id = int(input_id)
                    flag = False

    def create_toloka_project(self, sandbox=True):
        req = requests.post(self.url + 'projects', headers=self.headers, json=self.project_params)
        assert req.ok
        new_project_id = req.json()['id']
        print("New project was created. New project id: ", new_project_id)
        output_url = 'https://sandbox.toloka.yandex.ru/requester/project/{}' if sandbox \
            else 'https://toloka.yandex.ru/requester/project/{}'
        print(output_url.format(new_project_id))
        if self.project_id is None:
            self.project_id = new_project_id
        return new_project_id

    def update_toloka_project(self, project_id):
        req = requests.put(self.url + f'projects/{project_id}', headers=self.headers, json=self.project_params)
        if req.ok:
            print('The project was successfully updated')

    def create_toloka_pool(self, sandbox=True, pool_from_file=False, pool_params=None):
        if pool_from_file:
            with open('pool_params.json', 'r', encoding='utf-8') as file:
                pool_params = json.load(file)
        req = requests.post(self.url + 'pools', headers=self.headers, json=pool_params)
        print(req.json())
        new_pool_id = req.json()['id']
        print("New pool was created. New pool id: ", new_pool_id)
        output_url = 'https://sandbox.toloka.yandex.ru/requester/pool/{}' if sandbox \
            else 'https://toloka.yandex.ru/requester/pool/{}'
        print(output_url.format(new_pool_id))
        if self.project_id is None:
            self.project_id = new_pool_id
        return new_pool_id

    def get_pools_params(self, return_ids=True):
        req = requests.get(self.url + 'pools', headers=self.headers)
        if req.ok:
            output = req.json()['items']
            if return_ids:
                return [[item['id'], item['status']] for item in req.json()['items']]
            return req.json()['items']

    def open_close_pool(self, pool_id, type: str):
        req_type = 'open' if type.lower() == 'open' else 'close'
        output = requests.post(self.url + f'pools{pool_id}/{req_type}', headers=self.headers)
        if output.ok:
            print(f'Pool {pool_id} | Operation {req_type.upper()} successfully done')
        try:
            print(output.json())
        except json.decoder.JSONDecodeError:
            print(f'Most likely, operation {type.upper()} has already been performed')

    def archive_object(self, object_type, object_id):
        req = requests.post(self.url + f'{object_type}s/{object_id}/archive', headers=self.headers)
        if req.ok:
            print(f'Your object: {object_type}-{object_id} successfully archived')


if __name__ == '__main__':
    handler = TolokaProjectHandler('AQAAAABVFx8TAAIbuv-O6f5F5UdQpaujoE7VnNk', project_id=64894)
    # project = handler.create_toloka_project()
    # handler.update_toloka_project(64894)
    # pool = handler.create_toloka_pool()
    # handler.open_close_pool(handler.get_pools_params(), 'close')
    print(*handler.get_pools_params())
    # handler.create_toloka_pool(pool_params=PoolCreator(handler.project_id).pool)
    # handler.archive_object('pool', 879560)
