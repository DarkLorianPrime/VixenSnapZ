import requests

#standart_test_url = "http://127.0.0.1:8000/api"
standart_test_url = "http://pictures.darklorian.ru/api"

def main(headers):
    response = requests.get(standart_test_url + "/frames/", headers=headers)
    assert response.status_code == 200
    print(response.json())


def with_auth():
    main({"Authorization": "Token 348c626e03c54c8292ae0b80575066e3"})


def without_auth():
    main({})


if __name__ == "__main__":
    # without_auth()
    with_auth()
