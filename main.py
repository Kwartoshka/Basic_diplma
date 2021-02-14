import requests
import json
import datetime
import operator
from progress.bar import IncrementalBar


class User:
    url = 'https://api.vk.com/method/'

    def __init__(self,
                 vk_id=None,
                 ya_token=None,
                 number=3,
                 vk_token='10b2e6b1a90a01875cfaa0d2dd307b7a73a15ceb1acf0c0f2a9e9c586f3b597815652e5c28ed8a1baf13c',
                 version='5.126',
                 ):
        self.number = number
        self.vk_token = vk_token
        self.ya_token = ya_token
        self.version = version
        self.params = {
            'access_token': self.vk_token,
            'v': self.version,
        }
        self.is_closed = requests.get(self.url + 'users.get',
                                      params={**self.params, **{'user_id': vk_id}}
                                      ).json()['response'][0]['is_closed']

        if id is None:
            self.id = requests.get(self.url + 'users.get',
                                   params=self.params
                                   ).json()['response'][0]['id']
        else:
            self.id = vk_id

        if self.is_closed:
            self.friends = 'ПРОФИЛЬ ЗАКРЫТ'
        else:
            self.friends = requests.get(self.url + 'friends.get',
                                        params={**self.params, **{'user_id': self.id}}
                                        ).json()['response']['items']

    def get_photos(self):

        if self.is_closed == True:
            return

        res = requests.get(self.url + 'photos.get',
                           params={
                               **self.params,
                               **{
                                   'owner_id': self.id,
                                   'album_id': 'profile',
                                   'extended': 1
                               }
                           }
                           ).json()['response']['items']

        photos_list = []
        image_names = []
        for photo in res:
            image_dict = photo['sizes'][-1]
            name = str(photo['likes']['count'])

            if name not in image_names:
                image_names.append(name)
                image_dict['name'] = name + '.jpg'
            else:
                image_dict['name'] = name + ' ' + str(datetime.date.today()) + '.jpg'

            image_dict['square'] = image_dict['height'] * image_dict['width']
            photos_list.append(image_dict)
        photos_list.sort(
            key=operator.itemgetter('square'),
            reverse=True
        )

        if self.number > len(photos_list):
            print('Вы хотите сохранить больше фото,\n'
                  'чем есть у данного пользователя.\n'
                  'Будут скачаны все фото, которые есть.')
            self.number = len(photos_list)

        photos_list = photos_list[0: self.number]
        photos_json = {'data': photos_list}
        return photos_json

    def upload(self):
        photos_list = self.get_photos()
        if photos_list is None:
            print('Профиль является закрытым.\nЗагрузка фото невозможна')
            return
        photos_list = photos_list['data']
        print('Список фото для отправки подготовлен')
        HEADERS = {'Authorization': self.ya_token}
        purums = {'path': str(self.id)}
        res = requests.put('https://cloud-api.yandex.net/v1/disk/resources', params=purums, headers=HEADERS)
        bar = IncrementalBar('Загрузка файлов на диск', max=len(photos_list))
        for photo in photos_list:
            path = str(self.id) + '/' + photo["name"]
            params = {
                'path': path,
                'url': photo['url']
            }
            resp = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                 params=params,
                                 headers=HEADERS)
            bar.next()
        print('\nЗагрузка на диск завершена!')
        return 'Done'

    def json(self):
        data = self.get_photos()
        if data is None:
            return
        file = str(self.id) + '.json'
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)

            print('.json файл создан!')


vk_id = input('Здравствуйте! Введите id пользователя: ')
ya_token = input('Введите токен Яндекс.Диска: ')
number = int(input('Сколько фотографий вы желаете сохранить? '))

a = User(vk_id, ya_token, number)
a.upload()
a.json()
