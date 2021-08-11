from src.toloka_handler import TolokaProjectHandler


def pipeline_new_pool_with_tasks(oauth_token, pool_name, overlap=None, verbose=True, project_params_path=None):
    '''
    Rough pipeline for creating a new pool (possibly with a new project) with task-suites
    :param oauth_token:
    :param pool_name:
    :param overlap:
    :param verbose:
    :param project_params_path:
    :return:
    '''
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_path=project_params_path)
    new_pool_id = handler.create_toloka_pool(private_name=pool_name)
    input_values = [{'image': '/segm-photos/bears.jpg',
                     'path': 'image'},
                    {'image': '/segm-photos/moscow.jpg',
                     'path': 'image'},
                    {'image': '/segm-photos/winter.jpg',
                     'path': 'image'}]
    new_suite_id = handler.create_task_or_suite(new_pool_id, object='task-suite', input_values=input_values)
    if overlap is not None:
        handler.change_task_suite_overlap(new_suite_id, overlap=overlap, object_type='task-suite')


def pipeline_new_pool_with_tasks_from_yadisk_proxy(oauth_token, pool_name, proxy_name,
                                                   verbose=True, project_params_path=None):
    '''
    Rough pipeline for creating a new pool (possibly with a new project) with task-suites from Ya.Disk proxy-folder
    :param oauth_token:
    :param pool_name:
    :param proxy_name:
    :param verbose:
    :param project_params_path:
    :return:
    '''
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_path=project_params_path)
    new_pool_id = handler.create_toloka_pool(private_name=pool_name)
    new_suite_id = handler.create_task_suite_from_yadisk_proxy(new_pool_id, proxy_name, object='task-suite')


def pipeline_for_new_project(oauth_token, project_params_path, verbose=True):
    '''
    Pipeline for creating a new project only
    :param oauth_token:
    :param project_params_path:
    :param verbose:
    :return:
    '''
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_path=project_params_path)
