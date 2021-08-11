# **AutoToloka**
AutoToloka is a Python library for hosting and controlling tasks of the Yandex.Toloka service 

## Installation
To install the latest version from PyPI:
```python
pip install -U autotoloka
```

# Getting started
### OAuth Token
For authorization, you need to get an OAuth token, you can get it on your Yandex.Toloka profile.

Profile -> External Services Integration -> Get OAuth token

### Proxy
If you want to use Yandex.Disk as a storage for your images, then you need a proxy. You can add proxy on your Yandex.Toloka profile.

Profile -> External Services Interation -> Yandex.Disk Integration -> Add Proxy

### Example
```python

from autotoloka_test import TolokaProjectHandler

OAUTH_TOKEN = 'your_token'

PATH_TO_PROJECT_PARAMS = 'path_to_project_parameters'
PATH_TO_POOL_PARAMS = 'path_to_pool_params'

POOL_ID = 'pool_id' # ID of the created pool
PROJECT_ID = 'project_id' # ID of the project that the pool was created for
SUITE_ID - 'suite_id' # ID of the created suite
TASK_ID = 'task_id' # ID of the created task

handler = TolokaProjectHandler(OAUTH_TOKEN)


# Creates Toloka project by configuration in a given file
handler.create_toloka_project(PATH_TO_PROJECT_PARAMS) 

# Updates the project, obtained by the handler
handler.update_toloka_project(PATH_TO_PROJECT_PARAMS) 

# Prints out project parameters
handler.get_project_params() 

# Creates Toloka pool by dictionary-stored or file-based configurations
handler.create_toloka_pool(PATH_TO_POOL_PARAMS) 

# Updates Toloka pool by given parameters
handler.update_pool(PATH_TO_POOL_PARAMS) 

# Prints and returns all available pools' parameters
handler.get_pools_params(less_info=True, only_current_project=True) 

# Opens or closes the required pool
handler.open_close_pool(handler.get_pools_params(), 'open') # also you can close pool, then write 'close'

# Creates either a Toloka task or a Toloka task-suite by dictionary-stored input values
handler.create_task_or_suite(POOL_ID, 'task-suite', input_values) 

# Creates either a Toloka task or a Toloka task-suite with data from Ya.Disk proxy-folder
handler.create_task_suite_from_yadisk_proxy(POOL_ID, OAUTH_TOKEN, 'test-photos/test1/',
                                              object='task-suite', tasks_on_suite=1) 

# Prints all available tasks or task-suites in the project
handler.get_toloka_tasks_suites(POOL_ID, 'task-suite') 

# Archives the given object by its ID and type
handler.archive_object('project', PROJECT_ID) # also you use archive_object for pools, then you need ('pool', POOL_ID)

# Changes the overlap of either the task or the task-suite, also is able to set infinite overlap
handler.change_task_suite_overlap(TASK_ID, number_of_overlap, 'task-suite') 

# Sends the signal to stop showing the task-suite by its ID
handler.stop_showing_task_suite(SUITE_ID) 

handler.get_answers(POOL_ID)

```

### Authors
The library created by [SHIFTLab CFT]( https://team.cft.ru/start/lab )