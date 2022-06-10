import requests

standart_test_url = "http://127.0.0.1:8000/api"


def main():
    response = requests.post(standart_test_url + "/registration/", data={"username": "darklorian1", "password": "112233"})
    assert response.status_code == 201
    print(response.json())


if __name__ == "__main__":
    main()
