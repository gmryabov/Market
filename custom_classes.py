import json
import random
import string
from typing import Any, Optional
import requests
from requests import Response


class Message:
    def __init__(self, raw_data: dict) -> None:
        """
        Объект message все взято из документации телеграмма
        https://core.telegram.org/bots/api
        Используется для получения message_id
        :param raw_data:
        """
        self.message_id: int = raw_data.get("message_id")
        self.message_thread_id: int = raw_data.get("message_thread_id")
        self._from: Any = raw_data.get("from")
        self.sender_chat: Any = raw_data.get("sender_chat")
        self.sender_boost_count: int = raw_data.get("sender_boost_count")
        self.sender_business_bot: Any = raw_data.get("sender_business_bot")
        self.date: int = raw_data.get("date")
        self.business_connection_id: str = raw_data.get("business_connection_id")
        self.chat: Any = raw_data.get("chat")
        self.forward_origin: Any = raw_data.get("forward_origin")
        self.is_topic_message: bool = raw_data.get("is_topic_message")
        self.is_automatic_forward: bool = raw_data.get("is_automatic_forward")
        self.reply_to_message: Any = raw_data.get("reply_to_message")
        self.external_reply: Any = raw_data.get("external_reply")
        self.quote: Any = raw_data.get("quote")
        self.reply_to_story: Any = raw_data.get("reply_to_story")
        self.via_bot: Any = raw_data.get("via_bot")
        self.edit_date: int = raw_data.get("edit_date")
        self.has_protected_content: bool = raw_data.get("has_protected_content")
        self.is_from_offline: bool = raw_data.get("is_from_offline")
        self.media_group_id: str = raw_data.get("media_group_id")
        self.author_signature: str = raw_data.get("author_signature")
        self.text: str = raw_data.get("text")
        self.entities: list[Any] = raw_data.get("entities")
        self.link_preview_options: Any = raw_data.get("link_preview_options")
        self.effect_id: str = raw_data.get("effect_id")
        self.animation: Any = raw_data.get("animation")
        self.audio: Any = raw_data.get("audio")
        self.document: Any = raw_data.get("document")
        self.paid_media: Any = raw_data.get("paid_media")
        self.photo: list[Any] = raw_data.get("photo")
        self.sticker: Any = raw_data.get("sticker")
        self.story: Any = raw_data.get("story")
        self.video: Any = raw_data.get("video")
        self.video_note: Any = raw_data.get("video_note")
        self.voice = raw_data.get("voice")
        self.caption = raw_data.get("caption")
        self.caption_entities = raw_data.get("caption_entities")
        self.show_caption_above_media = raw_data.get("show_caption_above_media")
        self.has_media_spoiler = raw_data.get("has_media_spoiler")
        self.contact = raw_data.get("contact")
        self.dice = raw_data.get("dice")
        self.game = raw_data.get("game")
        self.poll = raw_data.get("poll")
        self.venue = raw_data.get("venue")
        self.location = raw_data.get("location")
        self.new_chat_members = raw_data.get("new_chat_members")
        self.left_chat_member = raw_data.get("left_chat_member")
        self.new_chat_title = raw_data.get("new_chat_title")
        self.new_chat_photo = raw_data.get("new_chat_photo")
        self.delete_chat_photo = raw_data.get("delete_chat_photo")
        self.group_chat_created = raw_data.get("group_chat_created")
        self.supergroup_chat_created = raw_data.get("supergroup_chat_created")
        self.channel_chat_created = raw_data.get("channel_chat_created")
        self.message_auto_delete_timer_changed = raw_data.get("message_auto_delete_timer_changed")
        self.migrate_to_chat_id = raw_data.get("migrate_to_chat_id")
        self.migrate_from_chat_id = raw_data.get("migrate_from_chat_id")
        self.pinned_message = raw_data.get("pinned_message")
        self.invoice = raw_data.get("invoice")
        self.successful_payment = raw_data.get("successful_payment")
        self.users_shared = raw_data.get("users_shared")
        self.chat_shared = raw_data.get("chat_shared")
        self.connected_website = raw_data.get("connected_website")
        self.write_access_allowed = raw_data.get("write_access_allowed")
        self.passport_data = raw_data.get("passport_data")
        self.proximity_alert_triggered = raw_data.get("proximity_alert_triggered")
        self.boost_added = raw_data.get("boost_added")
        self.chat_background_set = raw_data.get("chat_background_set")
        self.forum_topic_created = raw_data.get("forum_topic_created")
        self.forum_topic_edited = raw_data.get("forum_topic_edited")
        self.forum_topic_closed = raw_data.get("forum_topic_closed")
        self.forum_topic_reopened = raw_data.get("forum_topic_reopened")
        self.general_forum_topic_hidden = raw_data.get("general_forum_topic_hidden")
        self.general_forum_topic_unhidden = raw_data.get("general_forum_topic_unhidden")
        self.giveaway_created = raw_data.get("giveaway_created")
        self.giveaway = raw_data.get("giveaway")
        self.giveaway_winners = raw_data.get("giveaway_winners")
        self.giveaway_completed = raw_data.get("giveaway_completed")
        self.video_chat_scheduled = raw_data.get("video_chat_scheduled")
        self.video_chat_started = raw_data.get("video_chat_started")
        self.video_chat_ended = raw_data.get("video_chat_ended")
        self.video_chat_participants_invited = raw_data.get("video_chat_participants_invited")
        self.web_app_data = raw_data.get("web_app_data")
        self.reply_markup = raw_data.get("reply_markup")
        self.raw_data = raw_data

    def __str__(self):
        text = ""
        for _k, _v in self.raw_data.items():
            text += f"{_k}: {_v}\n"
        return text


class Telegram:
    def __init__(self, token: str, chat_id: int):
        """
        Основной объект для работы с телеграм, рассылкой отчетов
        :param token:
        :param chat_id:
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_telegram(self, text: str, link: str = None, chat_id: int = None) -> Message:
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id or self.chat_id,
                "text": text,
                "parse_mode": "Markdown"}
        if link:
            data["reply_markup"] = json.dumps({'inline_keyboard': [[{'text': 'Открыть в браузере', 'url': link}]]})
        r = requests.post(url, data=data)
        return Message(r.json().get('result'))

    def edit_message(self, text: str, message_id: int, link: str) -> None:
        requests.post(f"{self.base_url}/editMessageText", data={
            'chat_id': self.chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'Markdown',
            'reply_markup': json.dumps({
                'inline_keyboard': [[{
                    'text': 'Открыть в браузере',
                    'url': link,
                }]]
            })
        })

    def send_document(self, _route: str) -> Response:
        return requests.post(f"{self.base_url}/sendDocument",
                             files={"document": open(_route, 'rb')},
                             data={"chat_id": self.chat_id})

    def send_media(self, path: list, text: str) -> Message:
        url = f"{self.base_url}/sendMediaGroup"
        data = {
            "chat_id": self.chat_id,
            "media": [],
        }
        files = {}
        for route in path:
            fname = self.generate_random_token()
            files[fname] = open(route, 'rb')
            data['media'].append({'type': 'document',
                                  'media': f"attach://{fname}",
                                  # "caption": text,
                                  "parse_mode": "Markdown"})
        data['media'][0]["caption"] = text
        data['media'] = json.dumps(data['media'])

        resp = requests.post(url, data=data, files=files)
        if resp.status_code != 200:
            raise Exception(resp.json())
        if isinstance(resp.json().get('result'), list):
            return Message(resp.json().get('result')[0])
        return Message(resp.json().get('result'))

    def edit_mesg_media(self, mes_id: int, path: str, text: str):
        url = f"{self.base_url}/editMessageMedia"
        fname = self.generate_random_token()
        data = {
            "chat_id": self.chat_id,
            "message_id": mes_id,
            "media": {'type': 'document',
                      'media': f"attach://{fname}",
                      "caption": text,
                      "parse_mode": "Markdown"}
        }
        files = {fname: open(path, 'rb')}
        data['media'] = json.dumps(data['media'])
        resp = requests.post(url, data=data, files=files)
        if resp.status_code != 200:
            raise Exception(resp.json())
        return Message(resp.json().get('result'))

    @staticmethod
    def generate_random_token():
        return ''.join(random.sample(string.ascii_letters, 16))


class Nomenclature:
    def __init__(self,
                 name: str,
                 article: str,
                 category: str,
                 basic_price: float | int,
                 stock: int | float,
                 vendor: str,
                 yandex_category: Optional[str] = None,
                 yandex_price: Optional[float | int] = None,
                 yandex_commission: Optional[float] = None,
                 ozon_category: Optional[str] = None,
                 ozon_price: Optional[str] = None,
                 ozon_commission: Optional[float] = None,
                 mega_price: Optional[float | int] = None,
                 mega_category: Optional[str] = None,
                 mega_commission: Optional[float] = None,
                 site_category_id: Optional[int] = None,
                 warehouse: Optional[str] = None,
                 barcode: Optional[Any] = None,
                 group: Optional[str] = None,
                 pictures: Optional[list[str]] = None,
                 description: Optional[str] = None,
                 delivery_price: Optional[float | int] = None,
                 compensation: Optional[float | int] = None,
                 is_partner: Optional[bool] = None,
                 ):
        """
        Объект номенклатура
        :param name: Наименование номенклатуры
        :param article: Артикул товара
        :param category: Категория 1С
        :param basic_price: Закуп
        :param stock: Остаток
        :param vendor: Бренд
        :param yandex_category: Категория Яндекс (Для поиска комиссии)
        :param yandex_price: Цена для яндекса
        :param yandex_commission: Комиссия яндекса
        :param ozon_category: Категория озон (Для поиска комиссии)
        :param ozon_price: Цена для озон
        :param ozon_commission: Комиссия для озона
        :param mega_price: Цена для мегамаркета
        :param mega_category: Категория на мегамаркете (Для поиска комиссии)
        :param mega_commission: Комиссия на мегамаркете
        :param site_category_id: Айди категории на сайте (Для фида мегамаркета)
        :param warehouse: Склад (для отчета гугла)
        :param barcode: Штрихкод (для создания товара на МП)
        :param group: Ценовая группа 1с (для категории)
        :param pictures: Список изображений (для создания товара на МП)
        :param description: Описание товара
        :param delivery_price: Стоимость доставки (для отчета в гугле)
        :param compensation: Компенсация (для отчета в гугле)
        :param is_partner: Для партнерской номенклатуры (для отчета в телеге(
        """
        self.name = name
        self.article = article
        self.group = group
        self.category = category
        self.basic_price = basic_price
        self.stock = stock
        self.pictures = pictures
        self.description = description
        self.barcode = barcode
        self.vendor = vendor
        self.delivery_price = delivery_price
        self.compensation = compensation
        self.yandex_category = yandex_category
        self.yandex_price = yandex_price
        self.yandex_commission = yandex_commission
        self.ozon_category = ozon_category
        self.ozon_price = ozon_price
        self.ozon_commission = ozon_commission
        self.mega_price = mega_price
        self.mega_category = mega_category
        self.site_category_id = site_category_id
        self.warehouse = warehouse
        self.mega_commission = mega_commission
        self.is_partner = is_partner

    def __str__(self):
        return str(self.__dict__)


class FilterItems:
    """
    Фильтр для товаров, при выгрузке на маркетплейс
    """

    def __init__(self,
                 ignore_delivery: bool = False,
                 save_stock: list[str] = None,
                 outer: bool = None,
                 price_over: int = None,
                 stop_list: list[str] = None,
                 manage_stocks: bool = True,
                 target_filter: str = None):
        """
        :param ignore_delivery: Игнорирование стоимости доставки (Для самовывоза из Балтии Молл)
        :param save_stock: Сохранение остатков
        :param outer: Используем для РФ склада
        :param price_over: Ограничение по цене, если выше, то убрать остаток
        :param stop_list: Ограничение по типу товара, перечисление ключевых слов, которые мы не хотим грузить на МП
        :param manage_stocks: Регулирование остатков, можно отключить, получим истинные остатки для МП
        :param target_filter: Таргетировнанный фильтр, чтобы убрать остаток для конкретного товара
        """
        self.save_stock = save_stock
        self.outer = outer
        self.ignore_delivery = ignore_delivery
        self.price_over = price_over
        self.stop_list = stop_list
        self.manage_stocks = manage_stocks
        self.target_filter = target_filter


def to_json(obj, style: bool = False):
    """
    Создаем из любого кастомного объекта словарь, где ключ это переменные объекта, а значения - значение переменной
    :param style: Если True, ключи будут в lowerCamelCase
    :param obj: Объект для преобразования
    :return: Преобразованный объект в формате JSON
    """

    def replacer(s):
        return ''.join(c.upper() if i > 0 and s[i - 1] == '_' else c for i, c in enumerate(s) if c != '_')

    if isinstance(obj, dict):
        result = {}
        for key, val in obj.items():
            if val is not None:
                new_key = replacer(key) if style else key
                result[new_key] = to_json(val, style)
        return result
    elif isinstance(obj, list):
        return [to_json(t, style) for t in obj if t is not None]
    elif hasattr(obj, '__dict__'):
        return {replacer(k) if style else k: to_json(v, style) for k, v in obj.__dict__.items() if v is not None}
    else:
        return obj
