import os
import json

import requests
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

access_token = os.getenv('VK_TOKEN')













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
        if (vk.users_info(user_id)['response'][0]['first_name'].lower()) not in ['deleted', 'banned']:
            all_profile_photos = vk.photos_profile_info(user_id, album_id)
            photos = get_vk_photos(user_id, album_photos=all_profile_photos)
            try:
                load_photos_yd(user_id=user_id,
                               yd_token=yd_token,
                               photos_list=photos,
                               count=count)
            except Exception:
                print('Ошибка загрузки фото на сервер')
            print('-' * 100)
        else:
            raise Exception
    except Exception:
        print('Не удалось получить доступа к аккаунту ВК или он был удален.')



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

