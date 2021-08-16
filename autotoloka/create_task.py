import json
import random as rd


class TaskCreator:
    def __init__(self, pool_id, input_value):
        self.task = {
            'pool_id': pool_id,
            'input_values': input_value
        }


class TaskSuiteCreator:
    def __init__(self, pool_id, input_values=None):
        tasks = []
        if input_values is not None:
            for item in input_values:
                tasks.append(TaskCreator(pool_id, item).task)
        self.task_suite = {
            'pool_id': pool_id,
            'tasks': tasks,
            'overlap': 1,
            'infinite_overlap': 'false'
        }