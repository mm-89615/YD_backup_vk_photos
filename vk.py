import json
import os

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class VK:
    def __init__(self, token, user_id, version='5.199'):
        """
        Инициализация объекта класса VK для использования API

        :param token: токен VK API
        :param user_id: ID пользователя VK
        :param version: версия VK API
        """
        self.token = token
        self.version = version
        self.user_id = user_id
        self.params = {'access_token': self.token,
                       'v': self.version,
                       }

    def get_users_info(self):
        """
        Метод для получения данных о пользователе VK

        :return: json файл с информацией о пользователе
        """
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.user_id,
                  'fields': 'deactivated'}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_albums_info(self):
        """
        Метод для получения информации об альбомах пользователя VK

        :return: json файл с информацией об альбоме
        """
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'owner_id': self.user_id,
                  'need_system': 1}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def available_albums(self, response):
        """
        Метод для вывода информации об альбомах пользователя VK

        :param response: json файл с информацией об альбоме
        :return: множество с ID всех альбомов
        """

        print("Список всех альбомов:")
        albums_list = []
        albums_set = set()
        for album in response['response']['items']:
            album_date = {'id': album['id'],
                          'title': album['title'],
                          'size': album['size']
                          }
            albums_list.append(album_date)
            albums_set.add(album['id'])
        df = pd.DataFrame(albums_list)
        print(df)
        return albums_set

    def get_photos_info(self, album_id):
        """
       Метод для получения информации о фотографиях пользователя VK в альбоме

       :param album_id: ID альбома для получения фотографий
       :return: json файл с информацией о фотографиях с профиля пользователя
       """
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.user_id,
                  'album_id': album_id,
                  'extended': 1,
                  'photo_sizes': 1,
                  }
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_max_photos(self, album_photos):
        """
        Получение списка всех фотографий максимального размера.

        :param album_photos: Информация по всем фотографиям в альбоме
        :return: список json данных по каждой фотографии максимального размера
        """
        print("Список всех фотографий всех фотографий получен")
        photos_list = []
        # проход по каждой фотографии в альбоме
        for photos in album_photos['response']['items']:
            max_height = 0
            max_size_type = ''
            url_max_photo = ''
            # проход по каждому размеру отдельной фотографии
            for photo in photos['sizes']:
                # в файле встречаются размеры с 0 высотой, в таком случае
                # берется последний размер фотографии в списке
                if photo['height'] != 0:
                    if photo['height'] > max_height:
                        max_height = photo['height']
                        url_max_photo = photo['url']
                        max_size_type = photo['type']
                else:
                    url_max_photo = photo['url']
                    max_size_type = photo['type']
            # Информация каждой отдельной максимальной фотогографии
            data_photo = {
                'url': url_max_photo,
                'date': photos['date'],
                'type': max_size_type,
                'file_name': check_name(photos['likes']['count'], photos_list),
            }
            photos_list.append(data_photo)
        print(
            f"Список фотографий максимального размера получен.")
        return photos_list

    def download_photos(self, album_id, photos_list):
        """
        Сохранений фотографий из VK на компьютер

        :param album_id: ID альбома ВК
        :param photos_list: Список фотографий для сохранения
        :return:
        """
        # создает папку с именем == ID пользователя, если не создана
        if not os.path.isdir(f'{self.user_id}/{album_id}/'):
            os.makedirs(f'{self.user_id}/{album_id}/')
        for photo in photos_list:
            response = requests.get(photo['url'])
            file_path = f"{self.user_id}/{album_id}/{photo['file_name']}"
            if os.path.exists(file_path):
                with open(file_path, 'wb') as file:
                    file.write(response.content)


def check_name(name, photos_list):
    """
    Проверка на наличие уже имеющегося имени и переименование, если имеется

    :param name: Имя для проверки
    :param photos_list: Список имеющихся фотографий
    :return:
    """
    for photo_name in photos_list:
        file_name = photo_name['file_name'].split('.')[0]
        if str(name) == file_name:
            return f"{file_name}-{photo_name['date']}.jpg"
    return f"{name}.jpg"


def main():
    vk_token = input(
        'Введите токен VK API или нажмите ENTER, если токен внесен в файл .env: ')
    if not vk_token:
        vk_token = os.getenv('VK_TOKEN')
    user_id = input(
        'Введите ID пользователя VK в числовом формате (например, 1234515): ')
    vk = VK(vk_token, user_id)

    try:
        user_info = vk.get_users_info()
        if user_info.get('response') is None:
            raise ValueError
    except ValueError:
        print("Ошибка токена VK API TOKEN.")

    try:
        albums_info = vk.get_albums_info()
        if albums_info.get('response') is None:
            raise ValueError
        albums_set = vk.available_albums(albums_info)
    except ValueError:
        print("Ошибка получения информации о пользователе.")
    # album_id = -6
    album_id = input("Введите ID альбома VK (со знаком '-', если он есть): ")

    try:
        photos_info = vk.get_photos_info(album_id)
        if photos_info.get('response') is None:
            raise ValueError
        photo_list = vk.get_max_photos(photos_info)
    except ValueError:
        print("Ошибка получения информации о альбоме.")

    print(photo_list)
    # photos_list = vk.get_max_photos(vk.get_photos_info(album_id))
    # vk.download_photos(album_id,photos_list)


if __name__ == '__main__':
    main()
