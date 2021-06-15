from src.toloka_handler import TolokaProjectHandler


def pipeline_new_pool_with_tasks(oauth_token, pool_name, overlap=None, verbose=True, project_params_path=None):
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_path=project_params_path)
    new_pool_id = handler.create_toloka_pool(private_name=pool_name)
    input_values = [{'image': 'https://crosti.ru/patterns/00/12/02/4835fab2d8/picture.jpg'},
                    {'image': 'https://vignette.wikia.nocookie.net/calicoswarriorsrp/images/0/05/Stumpyboy.jpg/revision/latest?cb=20181217042736'},
                    {'image': 'https://i.pinimg.com/736x/09/04/b2/0904b2000fa6b0982167e799e91e4e08.jpg'}]
    new_suite_id = handler.create_task_or_suite(new_pool_id, object='task-suite', input_values=input_values)
    if overlap is not None:
        handler.change_object_overlap(new_suite_id, overlap=overlap, object_type='task-suite')


def pipeline_for_new_project(oauth_token, project_params_path, verbose=True):
    handler = TolokaProjectHandler(oauth_token, verbose=verbose, project_params_path=project_params_path)

if __name__ == '__main__':
    Greg, Arina = 'AQAAAABVFx8TAAIbuv-O6f5F5UdQpaujoE7VnNk', 'AQAAAAAOLepkAAIbukKmFBAvCkpluhXdXMFEyzo'
    # pipeline_new_pool_with_tasks(Greg, 'Test pool 3', overlap=2, verbose=False, project_params_path='project_params_2.json')
    pipeline_for_new_project(Greg, project_params_path='project_params_2.json')
