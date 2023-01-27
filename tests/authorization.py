import requests

standart_test_url = "http://127.0.0.1:8000/api/v1"
#standart_test_url = "http://pictures.darklorian.ru/api"


def main():
    response = requests.post(standart_test_url + "/login/", data={"username": "darklorian12", "password": "11223333F"})
    assert response.status_code == 200
    print(response.json())


if __name__ == "__main__":
    main()
