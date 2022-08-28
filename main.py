import configparser
from bd_ import add_writer, check_writer, check_count_photos, user_like, show_like_list, clear_like_list, get_next_user
from vk_ import Vk_writer
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import time

config = configparser.ConfigParser()
config.read('settings.ini')

GROUP_ID = config['vk']['GROUP_ID']
BOT_TOKEN = config['vk']['BOT_TOKEN']
API_VERSION = config['vk']['API_VERSION']

vk_session = VkApi(token=BOT_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

def loop():
    try:
        keyb_next = VkKeyboard(one_time=False, inline=True)
        keyb_like_next = VkKeyboard(one_time=False, inline=True)
        keyb_likelist_next = VkKeyboard(one_time=False, inline=True)
        keyb_clearlike_next = VkKeyboard(one_time=False, inline=True)

        keyb_next.add_callback_button(
            label="Next",
            color=VkKeyboardColor.PRIMARY,
            payload={"type": "next"},
        )
        keyb_like_next.add_callback_button(
            label="Like!",
            color=VkKeyboardColor.POSITIVE,
            payload={"type": "like"},
        )
        keyb_like_next.add_callback_button(
            label="Next",
            color=VkKeyboardColor.PRIMARY,
            payload={"type": "next"},
        )

        keyb_likelist_next.add_callback_button(
            label="Like list",
            color=VkKeyboardColor.POSITIVE,
            payload={"type": "likeList"},
        )
        keyb_likelist_next.add_callback_button(
            label="Next",
            color=VkKeyboardColor.PRIMARY,
            payload={"type": "next"},
        )
        keyb_clearlike_next.add_callback_button(
            label="Clear like list",
            color=VkKeyboardColor.NEGATIVE,
            payload={"type": "clear_like"},
        )
        keyb_clearlike_next.add_callback_button(
            label="Next",
            color=VkKeyboardColor.PRIMARY,
            payload={"type": "next"},
        )
        def send_message(user_id, text_message):
            vk.messages.send(
                        user_id = user_id,
                        random_id = get_random_id(),
                        message = text_message,
                        )

        f_toggle: bool = False
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                mess_text = event.obj.message["text"]
                writer_id = event.obj.message["from_id"]
                if not check_writer(writer_id):
                    if not isinstance(writer_id, Vk_writer):
                        writer_id = Vk_writer(writer_id)
                    if not hasattr(writer_id, 'age'):
                        if mess_text.isdigit():
                            send_message(writer_id.id,'Принято, чтобы подобрать пару, ответь "да" :)')
                            writer_id.age = int(mess_text)
                            add_writer(writer_id.id, writer_id.name, writer_id.age, writer_id.city_id, writer_id.sex_id)
                        else:
                            send_message(writer_id.id, {f'Привет, {writer_id.name}, введите свой возраст'})
                    else:
                        add_writer(writer_id.id, writer_id.name, writer_id.age, writer_id.city_id, writer_id.sex_id)
                        send_message(writer_id.id,{f'Привет, {writer_id.name}, чтобы подобрать пару, ответь "да" :)'})
                else:
                    writer_id = Vk_writer(writer_id)
                    if mess_text != "да" and mess_text != "Да":
                        send_message(writer_id.id,{f'Привет, {writer_id.name}, чтобы подобрать пару, ответь "да" :)'})

                    elif mess_text == "да" or mess_text == "Да":
                        if event.from_user:
                            send_message(writer_id.id,{f'{writer_id.name}, сейчас подберем вам пару. 1 минуту'})
                            if check_count_photos(writer_id.id) < 2:
                                writer_id.search_and_add_pairs()
                            next_user_list = get_next_user(writer_id.id)
                            vk.messages.send(
                                user_id=writer_id.id,
                                random_id=get_random_id(),
                                keyboard=keyb_like_next.get_keyboard(),
                                attachment = next_user_list[3],
                                message={f'{next_user_list[0]} {next_user_list[1]}\n https://vk.com/id{next_user_list[2]}'},
                            )
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                writer_id = event.obj["user_id"]
                writer_id = Vk_writer(writer_id)
                if event.object.payload.get("type") == "next":
                        next_user_list = get_next_user(writer_id.id)
                        time.sleep(0.5)
                        vk.messages.send(
                            user_id=writer_id.id,
                            random_id=get_random_id(),
                            keyboard=keyb_like_next.get_keyboard(),
                            attachment = next_user_list[3],
                            message={f'{next_user_list[0]} {next_user_list[1]}\n https://vk.com/id{next_user_list[2]}'},
                        )
                        if check_count_photos(writer_id.id) < 3:
                            writer_id.search_and_add_pairs()
                elif event.object.payload.get("type") == "like":
                    user_like(event.obj["user_id"],next_user_list[2])
                    vk.messages.send(
                            user_id=event.obj["user_id"],
                            random_id=get_random_id(),
                            keyboard=keyb_likelist_next.get_keyboard(),
                            message={f'{next_user_list[0]} {next_user_list[1]} - LIKE!'},
                        )
                elif event.object.payload.get("type") == "likeList":
                    mess = ''
                    ll = show_like_list(event.obj["user_id"])
                    for l in ll:
                        mess += f'{l[0]} {l[1]}\nhttps://vk.com/id{str(l[2])}\n'
                    vk.messages.send(
                            user_id=event.obj["user_id"],
                            random_id=get_random_id(),
                            keyboard=keyb_clearlike_next.get_keyboard(),
                            message=mess,
                        )
                elif event.object.payload.get("type") == "clear_like":
                    clear_like_list(event.obj["user_id"])
                    vk.messages.send(
                            user_id=event.obj["user_id"],
                            random_id=get_random_id(),
                            keyboard=keyb_next.get_keyboard(),
                            message='Like list очищен',
                        )
                    f_toggle = not f_toggle
        raise Exception
    except Exception as ex:
        print(ex)
        loop()

        
if __name__ == "__main__":
    loop()
    




