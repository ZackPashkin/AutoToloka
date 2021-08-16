import json
import random as rd


class PoolCreator:
    def __init__(self, project_id, private_name=f'Test_pool_{rd.randint(0,9999999)}',
                 may_contain_adult_content=False, will_expire='2030-01-01T13:00', reward_per_assignment=0.01,
                 assignment_max_duration_seconds=60*60, defaults=None, optional_params=None):
        if defaults is None:
            defaults = {'default_overlap_for_new_task_suites': 1,
                        'default_overlap_for_new_tasks': 3}
        else:
            defaults = {k: v for k, v in defaults.items()}
        self.pool = {'project_id': project_id,
                     'private_name': private_name,
                     'may_contain_adult_content': may_contain_adult_content,
                     'will_expire': will_expire,
                     'auto_close_after_complete_delay_seconds': 0,
                     'reward_per_assignment': reward_per_assignment,
                     'assignment_max_duration_seconds': assignment_max_duration_seconds,
                     'auto_accept_solutions': 'false',
                     'auto_accept_period_day': 1,
                     'assignments_issuing_config': {
                         'issue_task_suites_in_creation_order': 'false'
                     },
                     'defaults': defaults}
        if optional_params is not None:
            for k, v in optional_params.items():
                self.pool[k] = v

    def __str__(self):
        return json.dumps(self.pool, ensure_ascii=False, indent=4)

    def setup_optional_params(self, args: dict):
        for k, v in args.items():
            self.pool[k] = v

    def setup_dynamic_pricing(self, type=None, skill_id=None, intervals=None):
        if intervals is not None:
            intervals = [{'from': interval[0],
                                 'to': interval[1],
                                 'reward_per_assignment': interval[2]}for interval in intervals]
        dynamic_pricing_config = {'type': type,
                                  'skill_id': skill_id,
                                  'intervals': intervals}
        self.pool['dynamic_pricing_config'] = dynamic_pricing_config