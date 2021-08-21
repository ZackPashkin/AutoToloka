
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