from src.toloka_handler import TolokaProjectHandler


def pipeline_new_pool_with_tasks(oauth_token, pool_name, overlap=None, verbose=True, project_params_path=None):
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_path=project_params_path)
    new_pool_id = handler.create_toloka_pool(private_name=pool_name)
    input_values = [{'image': '/barkev2009/bears.jpg',
                     'path': 'image'},
                    {'image': '/barkev2009/moscow.jpg',
                     'path': 'image'},
                    {'image': '/barkev2009/winter.jpg',
                     'path': 'image'}]
    new_suite_id = handler.create_task_or_suite(new_pool_id, object='task-suite', input_values=input_values)
    if overlap is not None:
        handler.change_object_overlap(new_suite_id, overlap=overlap, object_type='task-suite')


def pipeline_for_new_project(oauth_token, project_params_path, verbose=True):
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_path=project_params_path)

if __name__ == '__main__':
    Greg, Arina = 'AQAAAABVFx8TAAIbuv-O6f5F5UdQpaujoE7VnNk', 'AQAAAAAOLepkAAIbukKmFBAvCkpluhXdXMFEyzo'
    pipeline_new_pool_with_tasks(Greg, 'Test pool 4', overlap=1, verbose=False, project_params_path='project_params_2.json')
    # pipeline_for_new_project(Greg, project_params_path='project_params_2.json')
