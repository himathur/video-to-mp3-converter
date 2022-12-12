import os
import requests
# requests are http calls thats need to me made


def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)
    basicAuth = (auth.username, auth.password)
    print(f"{basicAuth}")
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth
    )
    print(f" Response code from auth service : {response.code}")
    print(f" Response text from auth service : {response.text}")
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
