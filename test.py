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


y = YaDisk(token='AQAAAABVFx8TAAct8vFchXtyMETKokrzk1Q10XY')
files = list(y.listdir('Приложения/Toloka.Sandbox/autotoloka'))
print([file.name for file in list(y.listdir('Приложения/Toloka.Sandbox/autotoloka'))])
# for file in files:
#     print(file.name)
# y.remove('requirements.txt')