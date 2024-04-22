import json
import os

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DEFAULT_COUNT = 5
DEFAULT_ALBUM_ID = 'profile'


class VK:
    def __init__(self, token, user_id, version='5.131'):
        """
        Инициализация объекта класса VK для использования API.
        :param token: Токен VK API.
        :param user_id: ID пользователя VK.
        :param version: Версия VK API.
        :return: None.
        """
        self.token = token
        if not self.token:
            self.token = os.getenv('VK_TOKEN')
        self.version = version
        self.user_id = user_id
        self.album_id = None
        self.count_photo = None
        self.params = {'access_token': self.token, 'v': self.version}

    def set_album_id(self, album_id):
        """
        Метод для установки ID альбома.
        :param album_id: Id альбома.
        :return: None.
        """
        self.album_id = album_id

    def set_count_photo(self, count_photo):
        """
        Метод для установки количества фотографий для загрузки.
        :param count_photo: Количество фотографий для загрузки.
        :return: None.
        """
        self.count_photo = count_photo

    def get_users_info(self):
        """
        Метод для получения данных о пользователе VK.
        :return: Json файл с информацией о пользователе.
        """
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.user_id}
        try:
            response = requests.get(url, params={**self.params, **params})
            if response.json().get('response') is None:
                raise ValueError
            return response.json()
        except ValueError:
            print("Ошибка токена VK API TOKEN.")
            exit()

    def get_albums_info(self):
        """
        Метод для получения информации об альбомах пользователя VK.
        :return: Json файл с информацией об альбоме.
        """
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'owner_id': self.user_id,
                  'need_system': 1}
        try:
            response = requests.get(url, params={**self.params, **params})
            if response.json().get('response') is None or self.user_id == '':
                raise ValueError
            return response.json()
        except ValueError:
            print("Ошибка получения информации о пользователе.")
            exit()

    def get_photos_info(self):
        """
        Метод для получения информации о фотографиях пользователя VK в альбоме.
        :return: Json файл с информацией о фотографиях с профиля пользователя.
        """
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.user_id,
                  'album_id': self.album_id,
                  'count': self.count_photo,
                  'extended': 1,
                  'photo_sizes': 1,
                  }
        try:
            response = requests.get(url, params={**self.params, **params})
            if response.json().get('response') is None:
                raise ValueError
            return response.json()
        except ValueError:
            print("Ошибка получения информации об альбоме.")
            exit()

    def get_max_photos(self, album_photos):
        """
        Получение списка всех фотографий максимального размера.
        :param album_photos: Информация по всем фотографиям в альбоме.
        :return: Список json данных по каждой фотографии максимального размера.
        """
        print(f"Список всех фотографий из альбома '{self.album_id}' получен.")
        photos_list = []
        # проход по каждой фотографии в альбоме
        for photos in album_photos['response']['items']:
            max_height = 0
            max_size_type = ''
            url_max_photo = ''
            # проход по каждому размеру отдельной фотографии
            for photo in photos['sizes']:
                # в файле встречаются размеры с 0 высотой, в таком случае
                # берется последняя фотография в списке
                if photo['height'] != 0:
                    if photo['height'] > max_height:
                        max_height = photo['height']
                        url_max_photo = photo['url']
                        max_size_type = photo['type']
                else:
                    url_max_photo = photo['url']
                    max_size_type = photo['type']
            # Информация каждой отдельной максимальной фотографии
            data_photo = {
                'url': url_max_photo,
                'date': photos['date'],
                'type': max_size_type,
                'file_name': check_name(photos['likes']['count'], photos_list),
            }
            photos_list.append(data_photo)
        print(
            f"Список фотографий максимального размера сформирован ({len(photos_list)} фото).")
        return photos_list


def available_albums(response):
    """
    Метод для вывода информации об альбомах пользователя VK.
    :param response: Json файл с информацией об альбоме.
    :return: None.
    """
    print("Список всех альбомов:")
    albums_list = []
    for album in response['response']['items']:
        album_date = {'id': check_album_id(album['id']),
                      'title': album['title'],
                      'size': album['size']
                      }
        albums_list.append(album_date)
    df = pd.DataFrame(albums_list)
    print(df)


def check_album_id(album_id):
    """
    Изменение ID альбома для дальнейшего использования.
    :param album_id: Старый ID альбома.
    :return: Новый ID альбома.
    """
    # если пользователь не ввел никаких данных
    if not album_id:
        return DEFAULT_ALBUM_ID
    # ID альбома '-6' - фотографии профиля
    if album_id == -6:
        return 'profile'
    # ID альбома '-7' - фотографии со стены
    if album_id == -7:
        return 'wall'
    return album_id


def check_count(count):
    """
    Проверка на корректность ввода количества фотографий для загрузки.
    :param count: Количество фотографий для загрузки.
    :return: Количество фотографий для загрузки.
    """
    try:
        # если пользователь не ввел никаких данных
        if not count:
            return DEFAULT_COUNT
        count = int(count)
        if count > 0:
            return count
        raise ValueError
    except ValueError:
        print("Ошибка получения количества фотографий.")
        exit()


def check_name(name, photos_list):
    """
    Установка имени фотографии, а также проверка на дублирование.
    :param name: Имя для проверки.
    :param photos_list: Список имеющихся фотографий.
    :return: Имя фотографии.
    """
    for photo_name in photos_list:
        file_name = photo_name['file_name'].split('.')[0]
        if str(name) == file_name:
            return f"{file_name}-{photo_name['date']}.jpg"
    return f"{name}.jpg"


def download_photos(user_id, album_id, photos_list):
    """
    Сохранений фотографий из VK на компьютер.
    :param user_id: ID пользователя VK.
    :param album_id: ID альбома VK.
    :param photos_list: Список фотографий для сохранения.
    :return: None.
    """
    # создает папку с именем == ID пользователя, если не создана
    count_photo = 1  # счетчик всех фотографий
    downloaded_photos = 0  # счетчик загруженных фотографий
    print("Начинается загрузка фотографий...")
    # проверка на наличие папки
    if not os.path.isdir(f'{user_id}/{album_id}/'):
        print(f"Папка по пути '{user_id}/{album_id}/' создана.")
        os.makedirs(f'{user_id}/{album_id}/')
    for photo in photos_list:
        response = requests.get(photo['url'])
        file_path = f"{user_id}/{album_id}/{photo['file_name']}"
        # проверка на дублирование фотографий
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as file:
                file.write(response.content)
                downloaded_photos += 1
                print(
                    f"Фотография №{count_photo} - {photo['file_name']} загружена.")
        else:
            print(
                f"Фотография №{count_photo} - {photo['file_name']} уже существует.")
        count_photo += 1
    print(f"Загружено {downloaded_photos} фотографий из {len(photos_list)}.")


def main():
    # получение VK TOKEN и ID пользователя
    vk_token = input(
        'Введите токен VK API (если токен внесен в файл .env, нажмите ENTER): ')
    user_id = input(
        'Введите ID пользователя VK в числовом формате (например, 1234515): ')
    vk = VK(vk_token, user_id)
    # проверка на корректность ввода VK TOKEN
    vk.get_users_info()
    # вывод информации об альбомах, если ID пользователя корректен
    available_albums(vk.get_albums_info())
    # получение ID альбома VK и количества фотографий для загрузки
    album_id = input(
        "Введите ID альбома VK (по умолчанию - 'profile', нажмите ENTER): ")
    vk.set_album_id(check_album_id(album_id))
    count_photo = input(
        "Количество фотографий для загрузки (по умолчанию - 5, нажмите ENTER): ")
    vk.set_count_photo(check_count(count_photo))
    # получение списка фотографий максимального размера,
    # если ID альбома и количество для загрузки корректны
    photos_list = vk.get_max_photos(vk.get_photos_info())
    # скачивание на пк фотографий с VK
    download_photos(user_id, album_id, photos_list)


if __name__ == '__main__':
    main()
