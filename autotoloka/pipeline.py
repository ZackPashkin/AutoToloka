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
    new_suite_id = handler.create_task_suite(new_pool_id, input_values=input_values)
    if overlap is not None:
        handler.change_task_suite_overlap(new_suite_id, overlap=overlap)


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
    new_suite_id = handler.create_task_suite_from_yadisk_proxy(new_pool_id, proxy_name)


def pipeline_for_new_project(oauth_token, project_params_path, verbose=True):
    """
    Pipeline for creating a new project only

    :param oauth_token:
    :param project_params_path:
    :param verbose:
    """
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_data=project_params_path)


def pipeline_for_collecting_images(connect_to_existing_project=False, project_id=None,
                                   project_name="Let's collect some photos!", pool_name="Collecting images",
                                   number_of_images=5, general_description='Just choose some photo and upload it!',
                                   general_title='Photo to choose', progress_bar_length=60,
                                   oauth_token=None, download_folder_name='photos', verbose=False,
                                   check_for_duplicates=True, accept_and_reject_after_dedup=False,
                                   reject_errors=False):
    """
    Pipeline for collecting photos by Tolokers

    :param connect_to_existing_project: if set to True, connects to existing project
    :param project_id: ID of the project
    :param project_name: desired name of the new project
    :param pool_name: desired name of the new pool
    :param number_of_images: number of images to collect
    :param general_description: 'description' key for input_values (applies to a certain project configurations)
    :param general_title: 'product_title' key for input_values (applies to a certain project configurations)
    :param progress_bar_length: length of a progress bar
    :param oauth_token: token for connecting to Toloka API
    :param download_folder_name: name of a directory to download images to
    :param verbose: if set to True, prints out all the possible logs into the console
    :param check_for_duplicates: checks downloaded photos for duplicates
    :param accept_and_reject_after_dedup: processes tasks based on the results of deduplication
    :param reject_errors: if set to True, rejects task if a photo wasn't uploaded by the user
    """
    if connect_to_existing_project:
        handler = TolokaProjectHandler(oauth_token=oauth_token, project_id=project_id)
    else:
        collect_photos_config = json_data['collecting_images']
        collect_photos_config['public_name'] = project_name
        handler = TolokaProjectHandler(oauth_token=oauth_token, verbose=verbose,
                                       project_params_data=collect_photos_config)

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
    photo_data = handler.get_files_from_pool(pool_id, download_folder_name, reject_errors=reject_errors)
    if check_for_duplicates:
        handler.check_photos_for_duplicates(download_folder_name,
                                            reject_duplicates=accept_and_reject_after_dedup,
                                            photo_data=photo_data,
                                            accept_uniques=accept_and_reject_after_dedup)


if __name__ == '__main__':
    number_of_images, token, verbose = 10, 'AQAAAABVFx8TAAIbupmTNSLnLE9ostJWyUWHY-M', False
    pipeline_for_collecting_images(number_of_images=number_of_images,
                                   oauth_token=token,
                                   verbose=verbose,
                                   check_for_duplicates=True,
                                   accept_and_reject_after_dedup=True,
                                   reject_errors=True)
