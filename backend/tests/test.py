import os
import random
from unittest import TestCase

import httpx
files = []
for file in os.listdir("photos/"):
    files.append(("files", (open("photos/" + file, "rb"))))
print(files)
username = f"darklorian{random.randint(0, 1000)}"


access_token = []
files_created = []


class APITestCase(TestCase):
    def setUp(self) -> None:
        self.client = httpx.Client(base_url="http://127.0.0.1:8000/api/v1/")

    def test_1_registration(self):
        response = self.client.post("registration/", data={"username": username, "password": "11223344F"})
        response_json = response.json()
        assert response.status_code == 201
        assert response_json.get("id") is not None
        assert response_json.get("username") == username

    def test_2_authorization(self):
        response = self.client.post("login/", data={"username": username, "password": "11223344F"})
        response_json = response.json()
        assert response.status_code == 200
        assert response_json.get("access_token") is not None
        access_token.append(response_json.get("access_token"))

    def test_3_send_files_without_authorization(self):
        response = self.client.post("frames/", files=files)
        assert response.status_code == 401

    def test_4_send_files_with_authorization(self):
        headers = {"authorization": f"Bearer {access_token[0]}"}
        response = self.client.post("frames/", files=files, headers=headers)
        response_json = response.json()
        assert response.status_code == 201
        assert len(response_json) == 8
        files_created.extend(response_json)

    def test_5_get_file(self):
        headers = {"authorization": f"Bearer {access_token[0]}"}
        response = self.client.get(f"frames/{files_created[0]['server_name']}/", headers=headers)
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json.keys()) == 3

    def test_6_get_all_files(self):
        headers = {"authorization": f"Bearer {access_token[0]}"}
        response = self.client.get("frames/", headers=headers)
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 8

    def test_7_delete_file(self):
        headers = {"authorization": f"Bearer {access_token[0]}"}
        response = self.client.delete(f"frames/{files_created[0]['server_name']}/", headers=headers)
        assert response.status_code == 204

        response = self.client.get("frames/", headers=headers)
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 7
