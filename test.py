from yadisk import YaDisk
from yadisk.exceptions import BadRequestError
import sys


def get_token(id, password):
    y = YaDisk(id=id, secret=password)
    url = y.get_code_url()
    print("Go to the following url: %s" % url)
    code = input("Enter the confirmation code: ")

    try:
        response = y.get_token(code)
    except BadRequestError:
        print("Bad code")
        sys.exit(1)

    y.token = response.access_token
    if y.check_token():
        print("Sucessfully received token!")
        print(y.token)
    else:
        print("Something went wrong. Not sure how though...")
    return y.token

def print_kwargs(**kwargs):
    print(kwargs)
# get_token('5eff40921a664459ade80fa6c015ac6d', '30cec59d8626485d889e49841d41ef43')
# y = YaDisk(token='AQAAAABVFx8TAAct8n3WNOB0YUPipZmiDOHq9g4')
# print(y.check_token())
# files = list(y.listdir('Приложения/Toloka.Sandbox/autotoloka'))
# print([file.name for file in list(y.listdir('Приложения/Toloka.Sandbox/autotoloka'))])

# for file in files:
#     print(file.name)
# y.remove('requirements.txt')
print_kwargs(private_name=7, true_false=True)