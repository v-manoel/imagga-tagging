import requests
from constants import APISecrets


class RekognitionApiHandler:

    def __init__(self):
        # config options
        self.api_url = "https://api.imagga.com/v2/tags"
        self.language = "pt"
        self.version = "2"

    def set_queryset(self, image_url: str, limit: float = 15) -> None:
        self.query = {
            "image_url": image_url,
            "version": self.version,
            'language': self.language,
            'limit': limit
        }

    def set_headers(self) -> None:
        self.headers = {
            'accept': "application/json",
            'authorization': APISecrets.API_KEY

        }

    def request(self, image_url: str, limit: float) -> requests.Response:
        self.set_headers()
        self.set_queryset(image_url, limit)

        return requests.request(
            "GET",
            self.api_url,
            headers=self.headers,
            params=self.query)

    def get_image_tags(self, image_url: str, limit: float) -> list:
        response = self.request(image_url, limit).json()
        tags = response['result']['tags']

        tags_list = [
            {
                "name": tag['tag'][self.language],
                "confidence":tag['confidence']
            } for tag in tags
        ]

        return tags_list

    def get_images_batch_tags(self, images_url: list, limit: float) -> list:
        tags_list = []

        for url in images_url:
            image_tags = self.get_image_tags(url, limit)
            tags_list.append(
                {
                    "url": url,
                    "tags": image_tags
                }
            )

        return tags_list
