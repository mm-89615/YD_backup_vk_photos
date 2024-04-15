import os

import requests
import json
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

access_token = os.getenv('VK_TOKEN')
yd_token = os.getenv('YD_TOKEN')


class VK:
    def __init__(self, token, version='5.131'):
        self.token = token
        self.version = version
        self.params = {'access_token': self.token,
                       'v': self.version,
                       }

    def users_info(self, users_id):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': users_id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def photos_info(self, owner_id):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': owner_id,
                  'album_id': 'profile',
                  'extended': 1,
                  'photo_sizes': 1,
                  }
        response = requests.get(url, params={**self.params, **params})
        return response.json()


def get_photos(user_id):
    vk = VK(access_token)
    all_photos = vk.photos_info(user_id)
    photos_list = []

    for photos in all_photos['response']['items']:
        pprint(photos)
        data_photo = {}
        max_height = 0
        max_size_type = ''
        url_max_photo = ''
        for photo in photos['sizes']:
            if photo['height'] > max_height:
                max_height = photo['height']
                url_max_photo = photo['url']
                max_size_type = photo['type']

        data_photo['date'] = photos['date']
        data_photo['url'] = url_max_photo
        data_photo['type'] = max_size_type
        data_photo['likes'] = photos['likes']['count']
        photos_list.append(data_photo)
    return photos_list


def writing_json(photos_list):
    with open('photos.json', 'w', encoding='utf-8') as file:
        json.dump(photos_list, file, indent=4, ensure_ascii=False)

def get_json_list(photos_list):
    json_list = []
    for photo in photos_list:
        photo_info = {
            "file_name": f"{photo['likes']}.jpg",
            "size": photo['type'],
        }
        json_list.append(photo_info)

def main():
    user_id = '145001838'
    user_id_2 = '154533643'
    photos = get_photos(user_id)



    writing_json(get_json_list(photos))


if __name__ == '__main__':
    main()
