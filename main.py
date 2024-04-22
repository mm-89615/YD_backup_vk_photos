import os
import json

import requests

from vk import VK
from yandex_disk import YandexDisk


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
        os.makedirs(f"{user_id}/{album_id}/")
    for photo in photos_list:
        response = requests.get(photo['url'])
        file_path = f"{user_id}/{album_id}/{photo['file_name']}"
        # проверка на дублирование фотографий
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as file:
                file.write(response.content)
                downloaded_photos += 1
                print(f"Фотография №{count_photo}"
                      f" - {photo['file_name']} загружена.")
        else:
            print(f"Фотография №{count_photo}"
                  f" - {photo['file_name']} уже существует.")
        count_photo += 1
    print(f"Загружено {downloaded_photos} фотографий из {len(photos_list)}.")


def writing_json(user_id, album_id, photos_list):
    """
    Запись результата в JSON файл.
    :param user_id: ID пользователя ВК.
    :param album_id: ID альбома ВК.
    :param photos_list: Список загруженных фотографий.
    :return: None.
    """
    path_dir = f"json_files/{user_id}/"
    path_file = f"json_files/{user_id}/{album_id}.json"
    if not os.path.isdir(path_dir):
        os.makedirs(path_dir)
    with open(path_file, 'w', encoding='utf-8') as file:
        json.dump(photos_list, file, indent=4, ensure_ascii=False)
    print(f"Информация о загруженных фотографиях добавлена в json файл")


def main():
    # получение токена API VK и ID пользователя
    vk_token = input(
        "Введите токен VK API (если токен внесен в файл .env, нажмите ENTER): ")
    user_id = input(
        "Введите ID пользователя VK в числовом формате (например, 1234515): ")
    vk = VK(vk_token, user_id)
    photos_list = vk.get_photos_list()

    choice = input("""Куда загрузить фотографии?
- Введите 'пк' или 'pc' для скачивания на компьютер.
- Для загрузки на Яндекс.Диск нажмите ENTER.
""")

    if choice.lower() == 'пк' or choice.lower() == 'pc':
        # скачивание на пк фотографий с VK
        download_photos(user_id, vk.get_album_id(), photos_list)
    else:
        # получение токена API Яндекс.Диска
        yd_token = input("Введите токен API Яндекс.Диска "
                         "(если токен внесен в файл .env, нажмите ENTER): ")
        yd = YandexDisk(yd_token)
        yd.load_photos(user_id, vk.get_album_id(), photos_list)
        writing_json(user_id, vk.get_album_id(), photos_list)


if __name__ == '__main__':
    main()
