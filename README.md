# **AutoToloka**
AutoToloka is a Python library for hosting and controlling projects of the Yandex.Toloka service 


## Installation
To install the latest version from PyPI:
```python
pip install -U autotoloka
```

# Getting started

### See video demo here
[Docs page](https://zackpashkin.github.io/autotoloka.github.io)

### Quickstart
[Colab](https://colab.research.google.com/drive/1BYQJNkDpdGjUny-GwQeXew8jZFnyPt_Z?usp=sharing)


### OAuth Token
For authorization, you need to get an OAuth token from your Yandex.Toloka profile.
Go to:
Profile -> External Services Integration -> Get OAuth token

### Proxy
If you want to use Yandex.Disk as a storage (recommended) for your images, you need a proxy. You can add proxy on your Yandex.Toloka profile.
Go to:
Profile -> External Services Interation -> Yandex.Disk Integration -> Add Proxy

### Example
```python

from autotoloka import TolokaProjectHandler
from autotoloka.json_data import json_data

OAUTH_TOKEN = 'your_token'

PROJECT_CONFIG = json_data['project_name']

POOL_ID = 'pool_id' # ID of the created pool
PROJECT_ID = 'project_id' # ID of the project that the pool was created for
SUITE_ID = 'suite_id' # ID of the created suite

handler = TolokaProjectHandler(OAUTH_TOKEN)


# Creates Toloka project by configuration in a given file
handler.create_toloka_project(PROJECT_CONFIG) 

# Updates the project, obtained by the handler
handler.update_toloka_project(PROJECT_CONFIG) 

# Prints out project parameters
handler.get_project_params() 

# Creates Toloka pool by dictionary-stored or file-based configurations
handler.create_toloka_pool() 

# Updates Toloka pool by given parameters
handler.update_pool(POOL_ID) 

# Prints and returns all available pools' parameters
handler.get_pools_params(less_info=True, only_current_project=True) 

# Opens or closes the required pool
handler.open_close_pool(handler.get_pools_params()) # also you can close pool, then write 'close'

# Creates either a Toloka task or a Toloka task-suite by dictionary-stored input values
input_values = [{'key_1': 'value_1', 'key_2': 'value_2'}, 
                {'key_1': 'value_3', 'key_2': 'value_4'}]
handler.create_task_suite(POOL_ID, input_values) 

# Creates either a Toloka task or a Toloka task-suite with data from Ya.Disk proxy-folder
handler.create_task_suite_from_yadisk_proxy(POOL_ID, OAUTH_TOKEN, 'test-photos/test1/',
                                              tasks_on_suite=1) 

# Prints all available tasks or task-suites in the project
handler.get_toloka_tasks_suites(POOL_ID) 

# Archives the given object by its ID and type
handler.archive_object('project', PROJECT_ID) # also you use archive_object for pools, then you need ('pool', POOL_ID)

# Changes the overlap of either the task or the task-suite, also is able to set infinite overlap
handler.change_task_suite_overlap(SUITE_ID, overlap=1) 

# Sends the signal to stop showing the task-suite by its ID
handler.stop_showing_task_suite(SUITE_ID) 

handler.get_answers(POOL_ID)

```

### Authors
The library created by [SHIFTLab CFT]( https://team.cft.ru/start/lab )