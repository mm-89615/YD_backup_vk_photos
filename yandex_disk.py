import os

import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()


class YandexDisk:

    def __init__(self, token):
        """
        Инициализация объекта класса YandexDisk для использования API.
        :param token: Токен API Яндекс.Диска.
        :return: None.
        """
        self.token = token
        if not self.token:
            self.token = os.getenv('YD_TOKEN')
        self.headers = {'Authorization': self.token}

    def get_user_info(self):
        """
        Метод для получения информации о пользователе Яндекс.Диска.
        :return: Статус код об информации о пользователе:
                 200 - информация получена.
        """
        url = "https://cloud-api.yandex.net/v1/disk"
        try:
            response = requests.get(url, headers={**self.headers})
            if response.status_code == 200:
                return response.status_code
            raise ValueError
        except ValueError:
            print("Ошибка токена API Яндекс.Диска.")
            exit()

    def create_folder(self, user_id, album_id):
        """
        Создание папки на Яндекс.Диске.
        :param user_id: ID пользователя VK.
        :param album_id: ID альбома VK.
        :return Статус код создания папки:
                201 - папка создана.
                409 - папка уже существует.
        """
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        path_user = f"{user_id}/"
        path_album = f"{user_id}/{album_id}"
        try:
            params = {'path': path_user}
            response = requests.put(url, params=params,
                                    headers={**self.headers})
            if response.status_code not in {201, 409}:
                raise Exception
            params = {'path': path_album}
            response = requests.put(url, params=params,
                                    headers={**self.headers})
            if response.status_code not in {201, 409}:
                raise Exception
            print("Папка на Яндекс.Диске создана.")
        except Exception:
            print("Ошибка создания папки.")
            exit()

    def check_photo(self, path):
        """
        Проверка наличия файла на Яндекс.Диске.
        :param path: Путь к фотографии.
        :return: Статус код проверки:
                 200 - фотография есть в Яндекс.Диске.
                 404 - фотография отсутствует.
        """
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': path}
        try:
            response = requests.get(url, params=params,
                                    headers={**self.headers})
            if response.status_code not in {200, 404}:
                raise Exception
            return response.status_code
        except Exception:
            print("Не удалось получить информацию о фотографии на Яндекс.Диске")

    def upload_photo(self, path_photo, url_upload):
        """
        Загрузка фотографии на Яндекс.Диск по URL.
        :param path_photo: Путь куда загрузить фотографию.
        :param url_upload: URL откуда брать фотографию.
        :return: Статус код загрузки:
                 202 - фотография загружена.
        """
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {'path': path_photo,
                  'url': url_upload,
                  }
        try:
            response = requests.post(url, params=params,
                                     headers={**self.headers})
            if response.status_code == 202:
                return response.status_code
            raise Exception
        except Exception:
            print("Ошибка загрузки фотографии на Яндекс.Диск.")

    def upload_all_photos(self, user_id, album_id, photos_list):
        """
        Загрузка всех фотографий из списка на Яндекс.Диск.
        :param user_id: ID пользователя VK.
        :param album_id: ID альбома VK.
        :param photos_list: Список фотографий для загрузки.
        :return: None.
        """
        for photo in tqdm(
                photos_list,
                desc="Отправка фотографий на Яндекс.Диск",):
            path_photo = f"{user_id}/{album_id}/{photo['file_name']}"
            # проверка на существование фотографии
            if self.check_photo(path_photo) == 404:
                self.upload_photo(path_photo, photo['url'])

    def check_successful_downloads(self, user_id, album_id, photos_list):
        """
        Проверка загруженных фотографий.
        :param user_id: ID пользователя VK.
        :param album_id: ID альбома VK.
        :param photos_list: Список фотографий для загрузки.
        :return: Список загруженных фотографий.
        """
        uploaded_list = []  # список для записи в json
        count_files = 1  # счетчик фотографий
        uploaded_files = 0  # количество загруженных фотографий
        for photo in photos_list:
            # проверка появилось фото ли после загрузки
            path_photo = f"{user_id}/{album_id}/{photo['file_name']}"
            if self.check_photo(path_photo) == 200:
                photo_info = {
                    "file_name": photo['file_name'],
                    "size": photo['type'],
                }
                uploaded_files += 1
                uploaded_list.append(photo_info)
                print(f"Фотография №{count_files}"
                      f" - {photo['file_name']} загружено.")
            else:
                print(f"Фотография №{count_files}"
                      f" - {photo['file_name']} не удалось загрузить.")
            count_files += 1
        print(f"Загружено {uploaded_files} из {len(photos_list)} фотографий.")
        return uploaded_list

    def load_photos(self, user_id, album_id, photos_list):
        """
        Загрузка всех фотографий из списка на Яндекс.Диск.
        :param user_id: ID пользователя ВК.
        :param album_id: ID альбома ВК.
        :param photos_list: Список фотографий для загрузки.
        :return Список загруженных фотографий.
        """
        self.get_user_info()
        print(f"Идет процесс загрузки фотографий на Яндекс.Диск...")
        self.create_folder(user_id, album_id)
        self.upload_all_photos(user_id, album_id, photos_list)
        uploaded_list = self.check_successful_downloads(
            user_id,
            album_id,
            photos_list)
        return uploaded_list


def main():
    pass


if __name__ == '__main__':
    main()
