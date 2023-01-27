import requests

standart_test_url = "http://127.0.0.1:8000/api/v1"
#standart_test_url = "http://pictures.darklorian.ru/api"


def main(headers):
    response = requests.delete(standart_test_url + "/frames/110d6075-76b6-4efb-9c99-c91d0942c65f", headers=headers)
    assert response.status_code == 204
    print(response.json())


def with_auth():
    main({"Authorization": "Bearer 8aee418b-1c93-491a-9376-6c569d1d0d7f"})


def without_auth():
    main({})


if __name__ == "__main__":
    # without_auth()
    with_auth()
