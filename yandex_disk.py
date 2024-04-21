class YandexDisk:


    def __init__(self, token):
        self.token = token

    def yd_create_folder(user_id, yd_token):
        """
        Создание папки на Яндекс.Диске

        :param user_id: ID пользователя ВК
        """
        url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': user_id}
        headers = {'Authorization': yd_token}
        return requests.put(url_create_folder, params=params, headers=headers)

    def load_photos_yd(user_id, yd_token, photos_list, count):
        """
        Загрузка всех фотографий из списка на Яндекс.Диск

        :param user_id: ID пользователя ВК
        :param photos_list: Список фотографий для загрузки
        :param count: Количество загружаемых фотографий
        """
        try:
            response = yd_create_folder(user_id, yd_token)
            if response.status_code == 201 or response.status_code == 409:
                print('Папка на Яндекс.Диске создана.')

                url_upload_img = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
                headers = {'Authorization': yd_token}
                uploaded_list = []
                uploaded_files = 0  # количество загруженных фотографий
                count_files = check_count(count, photos_list)
                print(f"Идет процесс загрузки фотографий на Яндекс.Диск...")
                for i in range(0, count_files):
                    params = {
                        'path': f"{user_id}/{photos_list[i]['file_name']}",
                        'url': f"{photos_list[i]['url']}"
                    }
                    print(
                        f"Загружается {photos_list[i]['file_name']} в папку {user_id}\n"
                        f"URL фотографии: {photos_list[i]['url']}")

                    # информация по фотографии для записи в json файл
                    photo_info = {
                        "file_name": photos_list[i]['file_name'],
                        "size": photos_list[i]['type'],
                    }
                    try:
                        response = requests.post(url_upload_img, params=params,
                                                 headers=headers)
                        print(
                            f"Статус загрузки фотографии: {response.status_code}")
                        if response.status_code == 202:
                            uploaded_files += 1
                            uploaded_list.append(
                                photo_info)  # список для записи в json
                            print(
                                f"Загружено {uploaded_files} из {count_files} файлов")
                            print("-" * 100)
                        else:
                            raise Exception
                    except Exception:
                        print(
                            f"Не удалось загрузить файл {photos_list[i]['file_name']}")
                print(
                    f"Загружено {uploaded_files} из {count_files} фотографий пользователя.")
                return uploaded_list
            else:
                raise Exception
        except Exception:
            print('Ошибка процесса загрузки на Яндекс.Диск')

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
