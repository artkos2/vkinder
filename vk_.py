import configparser
import vk
import datetime
import time
from bd_ import check_user, add_new_pair_and_photos, add_writer, check_writer, get_writer

config = configparser.ConfigParser()
config.read('settings.ini')

USER_TOKEN = config['vk']['USER_TOKEN']
API_VERSION = config['vk']['API_VERSION']

vk_api = vk.API(access_token=USER_TOKEN, v=API_VERSION)

def get_photos(owner_id):
    res = vk_api.photos.get(owner_id= owner_id, album_id = 'profile', extended = 'likes')
    time.sleep(0.3)
    photo_list = []
    for photo in res['items']:
        photo_list.append([photo['id'],photo['likes']['count']])
    photos_list = sorted(photo_list, key=lambda x: x[1], reverse=True)
    if len(photos_list) >= 3:
        return [photos_list[0][0],photos_list[1][0],photos_list[2][0]]
    else:
        False
def user_city(city_name):
    res = vk_api.database.getCities(country_id = 1, q= city_name, count = 5)
    if res['count'] == 0:
        return False
    else:
        city_list = []
        for city in res['items']:
            if 'region' in city:
                city_list.append([city['id'], city['title'], city['region']])
            else:
                city_list.append([city['id'], city['title'], city['title']])
    return city_list
class Vk_writer:
    def __init__(self, writer_id):
        if not check_writer(writer_id):
            self.id = writer_id
            res = vk_api.users.get(user_id= self.id,fields = 'city, sex, bdate')
            self.name = res[0]['first_name']
            if 'city' in res[0]:
                self.city_id = int(res[0]['city']['id'])
            if int(res[0]['sex']) == 1:
                self.sex_id = 2
            elif int(res[0]['sex']) == 2:
                self.sex_id = 1
            if 'bdate' in res[0] and len(res[0]['bdate'].split('.')) > 2:
                self.age = int(datetime.datetime.now().year - int(res[0]['bdate'].split('.')[2]))
        else:  
            user_info = get_writer(writer_id)
            self.id = writer_id
            self.name = user_info[1]
            self.city_id = user_info[2]
            self.sex_id = user_info[3]
            self.age = user_info[4]

    def search_and_add_pairs(self):
        search_users_dict = {}
        offset = 0
        while len(search_users_dict) == 0:
            users = vk_api.users.search(sex = self.sex_id, city = self.city_id, status = 6, age_from = self.age - 1, age_to = self.age + 1, count = 20, offset = offset)
            for user in users['items']:
                if user['is_closed'] == False and not check_user(user['id']):
                    photos = get_photos(user['id'])
                    if photos:
                        search_users_dict[user['id']] = user['first_name'],user['last_name'], photos
            offset += 20
            time.sleep(0.3)
        add_new_pair_and_photos(search_users_dict, self.id)
        return 

    def add_writer_on_base(self):
        add_writer(self.id, self.name, self.age, self.city_id, self.sex_id)
        return 


# from pprint import pprint
# res = vk_api.database.getCities(country_id = 1, q= 'очер', count = 5)
# pprint(res)
# print(user_city('пермь'))