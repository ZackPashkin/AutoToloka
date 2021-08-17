from autotoloka.handler import TolokaProjectHandler
from autotoloka.json_data import json_data
import time
from sys import stdout


def pipeline_new_pool_with_tasks(oauth_token, pool_name, overlap=None, verbose=True, project_params_path=None):
    """
    Rough pipeline for creating a new pool (possibly with a new project) with task-suites

    :param oauth_token:
    :param pool_name:
    :param overlap:
    :param verbose:
    :param project_params_path:
    """
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_data=project_params_path)
    new_pool_id = handler.create_toloka_pool(private_name=pool_name)
    input_values = [{'image': '/segm-photos/bears.jpg',
                     'path': 'image'},
                    {'image': '/segm-photos/moscow.jpg',
                     'path': 'image'},
                    {'image': '/segm-photos/winter.jpg',
                     'path': 'image'}]
    new_suite_id = handler.create_task_suite(new_pool_id, object='task-suite', input_values=input_values)
    if overlap is not None:
        handler.change_task_suite_overlap(new_suite_id, overlap=overlap, object_type='task-suite')


def pipeline_new_pool_with_tasks_from_yadisk_proxy(oauth_token, pool_name, proxy_name,
                                                   verbose=True, project_params_path=None):
    """
    Rough pipeline for creating a new pool (possibly with a new project) with task-suites from Ya.Disk proxy-folder

    :param oauth_token:
    :param pool_name:
    :param proxy_name:
    :param verbose:
    :param project_params_path:
    """
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_data=project_params_path)
    new_pool_id = handler.create_toloka_pool(private_name=pool_name)
    new_suite_id = handler.create_task_suite_from_yadisk_proxy(new_pool_id, proxy_name, object='task-suite')


def pipeline_for_new_project(oauth_token, project_params_path, verbose=True):
    """
    Pipeline for creating a new project only

    :param oauth_token:
    :param project_params_path:
    :param verbose:
    """
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_data=project_params_path)


def pipeline_for_collecting_images(project_name="Let's collect some photos!", pool_name="Collecting images",
                                   number_of_images=5, general_description='Just choose some photo and upload it!',
                                   general_title='Photo to choose', progress_bar_length=60,
                                   oauth_token='AQAAAABVFx8TAAIbupmTNSLnLE9ostJWyUWHY-M',
                                   download_folder_name='photos', verbose=False):
    """
    Pipeline for collecting photos by Tolokers

    :param project_name: desired name of the new project
    :param pool_name: desired name of the new pool
    :param number_of_images: number of images to collect
    :param general_description: 'description' key for input_values (applies to a certain project configurations)
    :param general_title: 'product_title' key for input_values (applies to a certain project configurations)
    :param progress_bar_length: length of a progress bar
    :param oauth_token: token for connecting to Toloka API
    :param download_folder_name: name of a directory to download images to
    :param verbose: if set to True, prints out all the possible logs into the console
    """
    collect_photos_config = json_data['collecting_images']
    collect_photos_config['public_name'] = project_name
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_data=collect_photos_config)
    project_id = handler.project_id

    pool_id = handler.create_toloka_pool(private_name=pool_name)
    input_values = [{'product_title': general_title,
                     'description': general_description} for _ in range(number_of_images)]
    handler.create_task_suite(pool_id, input_values, tasks_on_suite=1)
    closed = handler.get_pools_params(pool_id).get('last_close_reason')
    handler.open_close_pool(pool_id)

    # Progress bar parameters
    bar, bar_length = '█', progress_bar_length
    bar_step = int(bar_length / len(input_values))

    while closed != 'COMPLETED':
        time.sleep(1)
        closed = handler.get_pools_params(pool_id).get('last_close_reason')
        active_tasks = handler.get_answers(pool_id)['items']
        statuses = [task['status'] for task in active_tasks]
        counter = statuses.count('SUBMITTED') if statuses else 0
        stdout.write('\rPhotos uploaded: {}/{} |{}{}|'.format(counter, len(input_values),
                                                              bar * bar_step * counter,
                                                              '-' * bar_step * (len(input_values) - counter)))
        stdout.flush()
    print('')
    handler.get_files_from_pool(pool_id, download_folder_name)
    # handler.open_close_pool(pool_id)
    handler.accept_all_tasks(pool_id)
    handler.archive_object('pool', pool_id)
    handler.archive_object('project', project_id)

