import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('VK_TOKEN')


class VK:
    def __init__(self, token, version='5.131'):
        """
        Инициализация объекта класса VK для использования API

        :param token: токен VK API
        :param version: версия VK API
        """
        self.token = token
        self.version = version
        self.params = {'access_token': self.token,
                       'v': self.version,
                       }

    def users_info(self, users_id):
        """
        Метод для работы с данными пользователя VK

        :param users_id: ID пользователя VK
        :return: json файл с информацией о пользователе
        """
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': users_id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def photos_profile_info(self, owner_id, album_id='profile'):
        """
       Метод для работы с данными фотографий с профиля пользователя VK

       :param owner_id: ID пользователя VK
       :param album_id: Название альбома для полученния данных:
                        'wall' - фотографии со стены
                        'profile' - фотографии профиля
       :return: json файл с информацией о фотографиях с профиля пользователя
       """
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': owner_id,
                  'album_id': album_id,
                  'extended': 1,
                  'photo_sizes': 1,
                  }
        response = requests.get(url, params={**self.params, **params})
        return response.json()


def get_vk_photos(user_id, album_photos):
    """
    Получение списка всех фотографий максимального размера.

    :param user_id: ID пользователя ВК
    :param album_photos: Информация по всем фотографиям в альбоме
    :return: список json данных по каждой фотографии максимального размера
    """
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
    print(f"Список фотографий пользователя {user_id} из профиля ВК получены.")
    return photos_list


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
            return f'{file_name}-{photo_name['date']}.jpg'
    return f'{name}.jpg'


def save_profile_photos(user_id, photos_list):
    """
    Сохранений фотографий из VK на компьютер

    :param user_id: ID пользователя ВК
    :param photos_list: Список фотографий для сохранения
    :return:
    """
    # создает папку с именем == ID пользователя, если не создана
    if not os.path.isdir(f'{user_id}/profile/'):
        os.makedirs(f'{user_id}/profile/')
    for photo in photos_list:
        response = requests.get(photo['url'])
        with open(f"{user_id}/profile/{photo['file_name']}", 'wb') as file:
            file.write(response.content)


def yd_create_folder(user_id, yd_token):
    """
    Создание папки на Яндекс.Диске

    :param user_id: ID пользователя ВК
    """
    url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
    params = {'path': user_id}
    headers = {'Authorization': yd_token}
    requests.put(url_create_folder, params=params, headers=headers)


def check_count(count, photos_list):
    """
    Проверка корректности количества

    :param count:
    :param photos_list:
    :return:
    """
    # если введено 'all' или больше длины списка, загружает все фото
    if count == 'all':
        return len(photos_list)
    elif int(count) < 0:
        return abs(count)
    elif int(count) >= len(photos_list):
        return len(photos_list)
    else:
        return count


def load_photos_yd(user_id, yd_token, photos_list, count):
    """
    Загрузка всех фотографий из списка на Яндекс.Диск

    :param user_id: ID пользователя ВК
    :param photos_list: Список фотографий для загрузки
    :param count: Количество загружаемых фотографий
    """
    yd_create_folder(user_id, yd_token)
    url_upload_img = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {'Authorization': yd_token}
    uploaded_list = []
    uploaded_files = 0  # количество загруженных фотографий
    count_files = check_count(count, photos_list)
    print(f"Идет процесс загрузки фотографий на Яндекс.Диск...")
    for i in range(0, count_files):
        params = {
            'path': f'{user_id}/{photos_list[i]['file_name']}',
            'url': f'{photos_list[i]['url']}'
        }
        # информация по фотографии для записи в json файл
        photo_info = {
            "file_name": photos_list[i]['file_name'],
            "size": photos_list[i]['type'],
        }
        try:
            requests.post(url_upload_img, params=params, headers=headers)
            uploaded_files += 1
            uploaded_list.append(photo_info)  # список для записи в json
            print(f"Загружено {uploaded_files} из {count_files} файлов")
        except Exception:
            print(f"Не удалось загрузить файл {photos_list[i]['file_name']}")
    print(
        f"Загружено {uploaded_files} из {count_files} фотографий пользователя.")
    writing_json(user_id, uploaded_list)


def writing_json(user_id, photos_list):
    """
    Запись результата в JSON файл

    :param user_id: ID пользователя ВК
    :param photos_list: Список загруженных фотографий
    """
    if not os.path.isdir('json_files/'):
        os.mkdir('json_files/')
    with open(f'json_files/{user_id}.json', 'w', encoding='utf-8') as file:
        json.dump(photos_list, file, indent=4, ensure_ascii=False)
    print(
        f"Информация о загруженных фотографиях добавлена в json файл")


def backup_photos(user_id, yd_token, count=5, album_id='profile'):
    """
    Получение информации о фотографиях с ВК по ID и названию альбома.
    Загрузка их на Яндекс.Диск

    :param user_id: ID пользователя ВК
    :param count: Количество фотографий для загрузки
    :param album_id: Альбом, откуда брать фотографии
    """
    vk = VK(access_token)
    try:
        # Попытка получить информацию о фотографиях по введенным данным
        all_profile_photos = vk.photos_profile_info(user_id, album_id)
        photos = get_vk_photos(user_id, album_photos=all_profile_photos)
    except Exception:
        print('Некорректный ввод данных')
    try:
        load_photos_yd(user_id=user_id,
                       yd_token=yd_token,
                       photos_list=photos,
                       count=count)
    except Exception:
        print('Ошибка загрузки фото на сервер')
    print('-' * 100)


def main():
    user_id = input('Введите ID пользователя VK в числовом формат: ')
    yd_token = input("Введите токен c Полигона Яндекс.Диска.\n"
                     "Если токен загружен в .env файл, то нажмите ENTER.\n")
    count = input(
        "Введите количество загружаемых фотографий на Яндекс.Диск.\n"
        "Введите 'all', если хотите загрузить все.\n"
        "По умолчанию количество = 5. Нажмите ENTER.\n")
    album_id = input("Введите альбом откуда брать фотографии:\n"
                     "  'wall' - фотографии со стены\n"
                     "  'profile' - фотографии с профиля\n"
                     "По умолчанию альбом = 'profile'. Нажмите ENTER.\n")
    if yd_token == '':
        yd_token = os.getenv('YD_TOKEN')
    if count == '':
        count = 5
    if album_id == '':
        album_id = 'profile'
    backup_photos(user_id, yd_token, count=count, album_id=album_id)


if __name__ == '__main__':
    # backup_photos(user_id=1, count='all', album_id='profile')
    main()
