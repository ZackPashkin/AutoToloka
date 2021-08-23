import json
from autotoloka.json_data import json_data_path
from imagededup.methods import PHash


def get_chunks(array, chunk_number=0, by_length=False, chunk_length=0):
    '''
    Returns chunks of a list of items, either by a number of chunks or by the number of items in a chunk
    :param array:
    :param chunk_number:
    :param by_length:
    :param chunk_length:
    :return:
    '''
    chunks = []
    if by_length:
        for i in range(len(array)):
            if i % chunk_length == 0:
                try:
                    chunks.append(array[i: i + chunk_length])
                except Exception:
                    if i != 0:
                        chunks.append(array[i:])
                    else:
                        chunks.append(array)
    else:
        div = len(array) // chunk_number
        x = len(array) - div * chunk_number
        for i in range(x):
            chunks.append(array[i * (div + 1):(i + 1) * (div + 1)])
        for i in range(x * (div + 1), len(array), div):
            chunks.append(array[i:i + div])
    return chunks


def print_json(item, indent=4):
    """
    Pretty-prints the mutable item

    :param item: mutable item to print
    :param indent: indentation for print
    """
    print(json.dumps(item, indent=indent, ensure_ascii=False))


def write_config_to_json_files(config_data: dict, file_name: str):
    """
    Writes the json-like configuration data into a file and stores it in json_files directory

    :param config_data: a json-like dictionary
    :param file_name: a name of a file to store the configurations in
    """
    if file_name is None or file_name[-5:] == '.json':
        raise ValueError('Please, provide the file_name without specifying the format')
    with open(f'{json_data_path}/{file_name}.json', 'w') as file:
        json.dump(config_data, file, indent=4)


def check_for_duplicates(image_folder):
    phasher = PHash()
    encodings = phasher.encode_images(image_dir=image_folder)
    duplicates = phasher.find_duplicates(encoding_map=encodings)
