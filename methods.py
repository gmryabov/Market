import pprint
import time
import pandas as pd
import json
import math
# import imaplib
# import email
import os
import re
import random
import requests
import gspread
# from base64 import b64decode
from typing import Optional
from gspread import Cell, Client
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, ElementTree
from main.ozon import Ozon
# from main.ozon_types import PostingStatusType
from main.yandex import YandexMarket
from main.custom_classes import Nomenclature, Telegram, FilterItems, to_json
import xlsxwriter
from xlsxwriter.worksheet import Worksheet
# from main.yandex_types import OrderStatusType


def create_nomeclature(
        url: str,
        warehouse_name: str,
        df: pd.DataFrame = None,
        parner_data: dict = None,
) -> list[Nomenclature]:
    """
    Если используется внешняя таблица, то обязательно, нужно передать ее с ключами:
    KEYS article, stock, cost, item_name, group, subgroup
    :param parner_data:
    :param url:
    :param warehouse_name:
    :param df:
    :return:
    """
    # Тут функция определяет, использовать внешнюю табличку или загрузить локальную,
    # внешняя передается на вход, локальная всегда задана в функции ее не требуется указывать
    if df is None:
        dirr = os.path.dirname(os.path.realpath(__file__))
        _route = os.path.join(dirr, f"xls/{warehouse_name}.xlsx")
        df = pd.read_excel(_route)
    # обязательные ключи для работы с таблой, проверяем их наличие и выводим ошибку при их отсутствии.
    requred = ["article", "stock", "cost", "item_name", "subgroup"]
    check = [k for k in requred if k not in df]
    if check:
        raise Exception(f"Не хватает ключей {" ".join(check)}")
    # парсинг контента с сайта
    con = get_content(url)
    # этот кусок кода для передачи в табличу гугла
    replace_names = {"Склад Sony": "КЛД",
                     "Сохо": "КЛД СОХО",
                     "Склад Marvel РФ": "РФ Marvel",
                     "Склад Mi-life Европа": "КЛД",
                     "Склад Mi life Балтия": "КЛД", }
    warehouse = replace_names.get(warehouse_name) or warehouse_name
    # создания словаря номенклатур с парой артикул и объектом Nomenclature
    res: dict[str, Nomenclature] = {}
    # список артикулов, для того чтобы не воткнуться в дубль, может вызвать ошибку, которая будет ломать обновление
    articles = []
    for _, row in df.iterrows():
        # берем артикул и получаем контент с сайта
        article = row.get('article')
        content = con.get(article)
        # товар без остатка пропускаем
        if str(row.get('stock')) == "nan":
            continue
        # приводим все к необходимым типам
        cost = float(row.get('cost'))
        stock = int(row.get('stock'))
        # когда встречаем дубль, делаем среднюю цену между дублями и присваиваем уже в результате
        if article in articles:
            cost = (res[article].basic_price + cost) / 2
            res[article].basic_price = cost
            continue
        # определим какой товар выгоднее, наш или партнерский, берем артикул и сравниваем закуп у товаров
        # если партнерский окажется выгоднее, то берем остаток и цену партнерского товара
        is_partner = False
        if parner_data:
            item = parner_data.get(article)
            if item:
                partner_cost = item.get('price')
                partner_stock = item.get('stock')
                if partner_cost and partner_stock:
                    if partner_cost < cost:
                        cost = partner_cost
                        stock = partner_stock
                        is_partner = True
        # создаем объект номенклатуры и записываем в итог
        nmcl = Nomenclature(
            article=article,
            stock=stock,
            basic_price=cost,
            warehouse=warehouse,
            is_partner=is_partner,
            name=row.get('item_name'),
            group=row.get('group'),
            category=row.get('subgroup'),
            site_category_id=content.get('categoryId') if content else None,
            description=content.get('description') if content else None,
            pictures=content.get('pictures') if content else None,
            barcode=content.get('barcode') if content else None,
            vendor=content.get('vendor') if content else None,
        )
        res[article] = nmcl
    return [v for v in res.values()]


def manage_table(warehouse_name: str, service: list[dict]):
    # таблицу с эски, превратим в нормальный формат
    repls = {"Market - Sc (XLSX)": "Sony",
             "Market - Europe (XLSX)": "Europe",
             "Market - Baltia (XLSX)": "Baltia"}
    dirr = os.path.dirname(os.path.realpath(__file__))
    remote_dir = "/home/odinass/data"
    _route = os.path.join(remote_dir, f"{warehouse_name}.xlsx")
    _df = pd.read_excel(_route)  # чтение таблицы
    _compensations = compensations(service)  # компенсации
    with open(os.path.join(dirr, f"json/{repls[warehouse_name]}.json"), "r") as f:
        _stocks = json.load(f)
    # присвоение каждой ячейке тип данных str
    for i in range(0, 3):
        _df[_df.columns[i]] = _df[_df.columns[i]].astype(str)
    # удаляем лишнее
    _df.columns = _df.iloc[0]
    # Сбрасываем первую строку т.к. это наименования таблицы
    _df = _df[1:]
    _df = _df.rename(columns={_df.columns[0]: 'article',
                              _df.columns[1]: 'compensation',
                              _df.columns[2]: 'item_name',
                              _df.columns[3]: 'group',
                              _df.columns[4]: 'stock',
                              _df.columns[5]: 'cost'})
    # удаляем None, так как это помешает созданию/обновлению товаров
    _df.dropna(axis=0, how='any', inplace=True)
    _df = _df[_df['article'] != 'Итого']
    _df['subgroup'] = _df["group"].apply(lambda x: str(x).split(" | ")[-1])
    _df['group'] = _df["group"].apply(lambda x: str(x).split(" | ")[0])
    # Если поставщик МКТ ООО, то заменим на True
    _df['compensation'] = _df['compensation'].apply(lambda x: True if x == 'МКТ ООО' else False)
    # проходимся по таблице, записываем в словарь, и записываем дубли
    # устанавливаем средний закуп, если есть дубль в словаре
    res = {}
    articles = []
    for i, row in _df.iterrows():
        article = row.get('article')
        cost = row.get('cost') / row.get('stock')
        if article in articles:
            res[article]["cost"] = (res[article]['cost'] + cost) / 2
        else:
            res[article] = {}
            res[article]["article"] = article
            is_cps = row.get('compensation')
            cps_val = 0
            if is_cps:
                cps_val = _compensations.get(article)
                res[article]["compensation"] = cps_val
            res[article]["item_name"] = row.get('item_name')
            res[article]["group"] = row.get('group')
            res[article]["subgroup"] = row.get('subgroup')
            res[article]["cost"] = cost - (cps_val if is_cps and cps_val else 0)
            articles.append(article)
        # актуальный остаток, в таблице есть свой, но он неверный, присваиваем остаток из отдельной, нормальной таблицы
        # если по артикулу ничего не найдено, то сносим с таблицы
        actual = _stocks.get(article)
        if not actual:
            _df.drop(i, inplace=True)
            continue
        else:
            res[article]["stock"] = actual
    # меняю наименования на те что использовались ранее, с эски прилетают на транслите
    rep = {"Market - Sc (XLSX)": "Склад Sony",
           "Market - Europe (XLSX)": "Склад Mi-life Европа",
           "Market - Baltia (XLSX)": "Склад Mi-life Балтия"}
    pd.DataFrame(res.values()).to_excel(os.path.join(dirr, f"xls/{rep[warehouse_name]}.xlsx"))


def make_stocks():
    """
    Читаем и форматируем таблицу в json файл, для дальнейшей работы с ней
    :return:
    """
    dirr = os.path.dirname(os.path.realpath(__file__))
    remote_dir = "/home/odinass/data"
    for filename in os.listdir(remote_dir):
        if 'stocks (XLSX).xlsx' in filename:
            path = os.path.join(remote_dir, f"{filename}")
            df = pd.read_excel(path)
            r = {row.get("Номенклатура.Артикул "): row.get("Количество") or 0
                 for _, row in df.iterrows()}
            name = re.match(r"(.*?) stocks ", filename).group(1)
            with open(os.path.join(dirr, f"json/{name}.json"), "w") as f:
                json.dump(r, f)
        else:
            continue


def setup_price(_items: list[Nomenclature],
                service: list[dict],
                warehouse_name: str,
                f: FilterItems = None,
                ) -> list[Nomenclature]:
    """
    Функция для установки цены на номенклатуре, для каждого МП
    :param _items:
    :param service:
    :param warehouse_name:
    :param f:
    :return:
    """
    if f is None:
        f = FilterItems()
    _commissions = commissions(service)  # комиссии
    _translate = translator(service)  # "Переводчик категорий"
    _compensations = compensations(service)  # значения компенсаций
    # Статичная цена, т.е. цена которая будет установлена приоритетно, вне зависимости от прочих значений
    _main_prices = main_price(service)
    # проходимся по каждой номенклатуре, и присваиваем ей категории МП
    _nomenclature = []
    res = {}
    dirr = os.path.dirname(os.path.realpath(__file__))
    for item in _items:
        translation = _translate.get(item.category)
        # если категорий нет для конкретного товара, то пропуск
        if not translation:
            continue
        item.ozon_category = translation.get('ozon_category')
        item.yandex_category = translation.get('yandex_category')
        item.mega_category = translation.get('mega_category')
        # значения комиссий по каждому маркету
        ozon_commissions = _commissions.get(item.ozon_category) if item.ozon_category != '' else None
        yandex_commissions = _commissions.get(item.yandex_category) if item.yandex_category != '' else None
        mega_commissions = _commissions.get(item.mega_category) if item.mega_category != '' else None
        # доставка, стандартная 800, для крупного 1000, для рф 1300
        delivery = 0 if f.ignore_delivery else 1300 if f.outer else 800 if "Телевизор" not in item.name else 1000
        # учет компенсации
        cps = _compensations.get(item.article)
        item.basic_price = item.basic_price - cps if cps and f.outer else item.basic_price
        # рассчитываем цену для маркетплейсов, если нет статичной стоимости для товара
        if item.article not in _main_prices:
            if ozon_commissions:
                item.ozon_price = generate_price(cost=item.basic_price,
                                                 commission=ozon_commissions,
                                                 delivery=delivery)
            if yandex_commissions:
                item.yandex_price = generate_price(cost=item.basic_price,
                                                   commission=yandex_commissions,
                                                   delivery=delivery)
            if mega_commissions:
                item.mega_price = generate_price(cost=item.basic_price,
                                                 commission=mega_commissions,
                                                 delivery=delivery)
        else:
            price = _main_prices.get(item.article)
            item.yandex_price = price
            item.ozon_price = price
            item.mega_price = price

        # конфигурация остатков
        if f.manage_stocks and not item.is_partner:
            # если передан стоп лист товаров, то убираем остаток, этих товаров не должно быть на ИП в итоге
            if f.stop_list:
                for part in item.name.split():
                    if part in f.stop_list:
                        # if (
                        #         item.ozon_price > f.price_over
                        #         or item.yandex_price > f.price_over
                        #         or item.mega_price > f.price_over
                        # ):
                        #     item.stock = 0
                        item.stock = 0
            # Если товар находится в списке для сохранения остатка, то сохраняем остаток
            # Если списка для сохранений нет, то от остатка отнимается 1
            if f.save_stock:
                item.stock = item.stock if [part for part in item.name.split() if part in f.save_stock] \
                    else item.stock - 1 if item.stock > 0 else 0
            else:
                # Таргетированный фильтр, если нужно вы
                if f.target_filter:
                    item.stock = item.stock - 1 if f.target_filter in item.name else item.stock
                else:
                    item.stock = item.stock - 1 if item.stock > 0 else 0
        # присваиваем всю инфу по товару
        item.delivery_price = delivery
        item.compensation = cps
        item.yandex_commission = yandex_commissions
        item.mega_commission = mega_commissions
        item.ozon_commission = ozon_commissions
        res[item.article] = item.__dict__
    # записываем в json для работы с отчетностью в гугле
    with open(os.path.join(dirr, f"json/{warehouse_name}.json"), "w") as f:
        json.dump(res, f)
    return _items


def generate_price(cost: int | float, commission: float, delivery: int, compensation=0, margin=0.1) -> float | int:
    """
    Основная формула расчета стоимости товара
    :param cost: закуп
    :param commission: комиссия
    :param delivery: стоимость доставки
    :param compensation: компенсация
    :param margin: маржа
    :return:
    """
    return math.ceil((cost - compensation + delivery) / (1 - margin - commission / 100) / 100) * 100 - 10


def client_credentials(service_acc: list[dict]) -> Client:
    """Функция для конекта с гуглтаблицей"""
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(random.choice(service_acc), scope)
    _client = gspread.authorize(credentials)
    return _client


# Функция для получения словаря комиссий формата Категория маркета: значение комиссии
def commissions(s) -> dict[str, float]:
    sheet = client_credentials(s).open("Комиссии Маркетплейсов").worksheet('Коммиссии')
    res = {}
    for left, right, in [("B", "C"), ("E", "F"), ("G", "H")]:
        cats = sheet.range(f"{left}:{left}")
        vals = sheet.range(f"{right}:{right}")
        for idx, cell in enumerate(vals):
            if cell.value == '':
                continue
            try:
                res[cats[idx].value] = float(cell.value) + 1
            except ValueError:
                continue
    return res


# Перевод категории 1С на категорию маркета формат Категория 1С: Категория Маркета
def translator(s) -> dict:
    sheet = client_credentials(s).open("Комиссии Маркетплейсов").worksheet("Сопоставления")
    subcategory = sheet.range("B:B")
    ozon_category = sheet.range("C:C")
    yandex_category = sheet.range("D:D")
    mega_category = sheet.range("E:E")
    res = {}
    for idx, cell in enumerate(subcategory):
        if cell.value == '':
            break
        res[cell.value] = {"ozon_category": ozon_category[idx].value,
                           "yandex_category": yandex_category[idx].value,
                           "mega_category": mega_category[idx].value}
    return res


# Компенсации в int значении, формат Артикул:int
def compensations(s) -> dict[str, int]:
    sheet = client_credentials(s).open("Комиссии Маркетплейсов").worksheet("Компенсации")
    articles = sheet.range(f"A:A")
    value = sheet.range(f"B:B")
    res = {}
    for idx, cell in enumerate(articles):
        if cell.value == '' or value[idx].value == '':
            continue
        try:
            res[cell.value] = int(value[idx].value)
        except ValueError:
            continue
    return res


def get_content(url) -> dict:
    """
    Функция для парсинга контента с сайта
    :param url:
    :return:
    """
    req = requests.get(url).text.encode('latin-1').decode('utf-8')
    bs = BeautifulSoup(req, 'xml')
    offers = bs.find("offers").find_all('offer')
    res = {}
    for __offer in offers:
        __offer = str(__offer)
        description = re.search(r'<description>(.*?)</description>', __offer)
        barcode = re.search(r'<barcode>(.*?)</barcode>', __offer)
        article = re.search(r'id="(.*?)"', __offer).group(1)
        vendor = re.search(r'<vendor>(.*?)</vendor>', __offer)
        res[article] = {'description': description if description is None else description.group(1),
                        'pictures': re.findall(r'<picture>(.*?)</picture>', __offer),
                        'barcode': barcode if barcode is None else barcode.group(1),
                        'vendor': vendor if vendor is None else vendor.group(1),
                        'article': article,
                        'categoryId': re.search(r'<categoryId>(.*?)</categoryId>', __offer).group(1)}
    return res


def make_order(
        items: list[Nomenclature],
        warehouse: str,
        tg: Telegram,
        raw_name=None,
        is_another: bool = False
) -> list:
    """
    Функция для создания таблички с отчетом и отправки в телегу
    :param items: Информация по товарам созданным в ходе работы скрипта
    :param warehouse: Название склада
    :param tg: Телега
    :param raw_name: Наименование склада без тега
    :param is_another: Для того чтобы дубли МП типа Экспресс и Пункт выдачи не формировали цены
    :return:
    """
    # структура таблицы
    res = {
        "Артикул": [],
        "Партнерский": [],
        "Наименование": [],
        "Остаток": [],
        "Закуп": [],
        "Компенсация": [],
        "Доставка": [],
        "Категория": [],
        "Цена Озон": [],
        "Комиссия Озон": [],
        "Категория Озон": [],
        "Цена Яндекс": [],
        "Комиссия Яндекс": [],
        "Категория Яндекс": [],
        "Цена Мега": [],
        "Комиссия Мега": [],
        "Категория Мега": []
    }
    for item in items:
        res['Артикул'].append(item.article)
        res['Партнерский'].append(f"{"Партнерский" if item.is_partner else ""}")
        res['Наименование'].append(item.name)
        res['Категория'].append(item.category)
        res['Остаток'].append(item.stock)
        res['Компенсация'].append(item.compensation)
        res['Закуп'].append(item.basic_price)
        res['Доставка'].append(item.delivery_price)
        res['Цена Озон'].append(item.ozon_price)
        res['Комиссия Озон'].append(item.ozon_commission)
        res['Категория Озон'].append(item.ozon_category)
        res['Цена Яндекс'].append(item.yandex_price)
        res['Комиссия Яндекс'].append(item.yandex_commission)
        res['Категория Яндекс'].append(item.yandex_category)
        res['Цена Мега'].append(item.mega_price)
        res['Комиссия Мега'].append(item.mega_commission)
        res['Категория Мега'].append(item.mega_category)


    # res = {"Артикул": [v.article for v in items],
    #        "Партнерский": [f"{"Партнерский" if v.is_partner else ""}" for v in items],
    #        "Наименование": [v.name for v in items],
    #        "Остаток": [v.stock for v in items],
    #        "Закуп": [v.basic_price for v in items],
    #        "Доставка": [v.delivery_price for v in items],
    #        "Категория": [v.category for v in items],
    #        "Цена Озон": [v.ozon_price for v in items],
    #        "Комиссия Озон": [v.ozon_commission for v in items],
    #        "Категория Озон": [v.ozon_category for v in items],
    #        "Цена Яндекс": [v.yandex_price for v in items],
    #        "Комиссия Яндекс": [v.yandex_commission for v in items],
    #        "Категория Яндекс": [v.yandex_category for v in items],
    #        "Цена Мега": [v.mega_price for v in items],
    #        "Комиссия Мега": [v.mega_commission for v in items],
    #        "Категория Мега": [v.mega_category for v in items]}
    # запись таблицы
    dirr = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dirr, f"xls/{warehouse} tg.xlsx")
    # В зависимости от склада, выбираем нужный тип цены для формирования таблицы цен в эску
    select_type = {
        "Склад Mi-life Европа Ozon Сохо": [PriceTypes.ozon_ko],
        "Склад Marvel РФ Озон и Яндекс": [PriceTypes.yandex_rf, PriceTypes.ozon_rf],
        "Склад Sony Пункт выдачи Озон": [PriceTypes.ozon_ko],
        "Склад Sony Экспресс Озон": [PriceTypes.ozon_ko],
        "Марвел Мегамаркет": [PriceTypes.mega_rf],
        "Склад Mi-life Балтия": [PriceTypes.mega_ko],
        "Склад Mi-life Европа": [PriceTypes.mega_ko],
        "Склад Sony": [PriceTypes.mega_ko],
        "Склад Mi-life Европа Ozon Express": [PriceTypes.ozon_ko],
        "Склад Mi-life Европа Ozon Пункт выдачи": [PriceTypes.ozon_ko],
        "Сохо": [PriceTypes.yandex_coxo],
        "Склад Mi-life Европа Яндекс": [PriceTypes.yandex_ko],
        "Склад Sony Яндекс и Озон": [PriceTypes.yandex_ko, PriceTypes.ozon_ko],
    }
    print("Отчет создан")
    _data = pd.DataFrame(res).sort_values(by=['Наименование', 'Категория'])
    _data.to_excel(path)
    # Формирование таблицы с видом цены для эски
    if raw_name and not is_another:
        # смена канала телеги до отправки таблички
        main = tg.chat_id
        tg.chat_id = -1002209119881
        print("Создание таблиц для установки цен")
        for t in select_type[warehouse]:
            print(f"Установка цены {t} - {raw_name}")
            file = f"{raw_name}_{t}"
            # создаем таблицу
            r = price_for_onec(df=_data, output_file_name=file, price_type=t)
            json_name = f"{file}.json"
            # Для записи id Сообщения, чтобы не было спама от бота
            _json = os.path.join(dirr, f"json/{json_name}")
            if json_name not in os.listdir(os.path.join(dirr, 'json')):
                mes = tg.send_media(path=[r], text=f"*Склад:* {raw_name}\n*Вид цены:* `{t}`")
                with open(_json, "w", encoding="utf-8") as f:
                    json.dump({"mes_id": mes.message_id}, f)
            else:
                with open(_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                tg.edit_mesg_media(data['mes_id'], r, text=f"*Склад:* {raw_name}\n*Вид цены:* `{t}`")
        # переключение чата обратно
        tg.chat_id = main
    return [path]


# def load_table(subject: str, service: list[dict] = None, stoks=False, ):
#     def dec(x: str) -> str:
#         _x = re.match(r'=\?utf-8\?B\?(.*?)\?=', x)
#         if _x is not None:
#             return b64decode(_x.group(1)).decode('utf-8')
#         return x
#
#     dirr = os.path.dirname(os.path.realpath(__file__))
#     mail = imaplib.IMAP4_SSL('imap.yandex.ru')
#     mail.login('gr@it-premium.com', 'Soli23sol!')
#     mail.select('INBOX')
#     result, data = mail.search(None, 'ALL')
#     ids = data[0]
#     id_list = ids.split()
#     id_list.reverse()
#     routes = []
#     for num in id_list:
#         result, data = mail.fetch(num, '(RFC822)')
#         raw_email = data[0][1]
#         msg = email.message_from_bytes(raw_email)
#         title: str = dec(msg['Subject'])
#         if title in subject:
#             for i, part in enumerate(msg.walk()):
#                 if part.get_content_maintype() == 'application' and part.get('Content-Disposition'):
#                     filename = dec(part.get_filename())
#                     path = os.path.join(dirr, f"{filename if stoks else subject}.xlsx")
#                     with open(path, 'wb') as f:
#                         f.write(part.get_payload(decode=True))
#                     routes.append(path)
#                     if not stoks:
#                         repls = {"Склад Sony": "Sony",
#                                  "Склад Mi-life Европа": "Europe",
#                                  "Склад Mi-life Балтия": "Baltia"}
#                         manage_table(subject, repls[subject], service)
#             break
#     mail.close()
#     mail.logout()
#     return routes


def from_gsheet_to_df(table: str, page: str, _range: str, *col_names: str, service: list[dict]) -> pd.DataFrame:
    """
    Создание датафрейма из гуглтаблицы
    :param table: Название таблицы в гугле
    :param page: Название страницы в таблице
    :param _range: Диапазон ячеек (их адреса)
    :param col_names: Итоговые названия столбцов
    :param service: Сервисные аккаунты
    :return:
    """
    _values: list[Cell] = client_credentials(service).open(table).worksheet(page).range(_range)
    table = {name: [] for name in col_names}
    rows = [_values[i:i + len(col_names)]
            for i in range(0, len(_values), len(col_names))
            if _values[i].value != '']
    for row in rows:
        for i, cell in enumerate(row):
            table[col_names[i]].append(cell.value)
    return pd.DataFrame(table)


def xml_tree_builder(categories: dict, _offers: list[Nomenclature], outlet_id: str, filename: str, path: str) -> str:
    # Создаем корневой элемент
    yml_catalog = Element('yml_catalog')
    yml_catalog.set("date", datetime.now().strftime("%Y-%m-%dT%H:%M+03:00"))
    # элемент shop
    shop = SubElement(yml_catalog, "shop")

    # элемент категории
    _categories = SubElement(shop, "categories")
    for _id, category_name in categories.items():
        category = SubElement(_categories, "category")
        category.set("id", str(_id))
        category.text = category_name

    # элемент offers
    offers = SubElement(shop, "offers")
    for nomenclature in _offers:
        if (not nomenclature.mega_price or not nomenclature.site_category_id
                or nomenclature.site_category_id not in categories):
            continue
        _offer = SubElement(offers, "offer")
        _offer.set("id", str(nomenclature.article))
        _offer.set("type", "vendor.model")
        _offer.set("available", "true")
        SubElement(_offer, "price").text = str(nomenclature.mega_price)
        SubElement(_offer, "vendor").text = nomenclature.vendor or ""
        SubElement(_offer, "vendorCode").text = str(nomenclature.article)
        SubElement(_offer, "barcode").text = nomenclature.barcode or ""
        SubElement(_offer, "model").text = nomenclature.name or ""
        SubElement(_offer, "description").text = nomenclature.description or ""
        SubElement(_offer, "categoryId").text = nomenclature.site_category_id
        SubElement(_offer, "count").text = f"{nomenclature.stock}" or "0"
        _outlets = SubElement(_offer, "outlets")
        outlet = SubElement(_outlets, "outlet")
        outlet.set("id", outlet_id)
        outlet.set("instock", f"{nomenclature.stock}")
        outlet.set("price", f"{nomenclature.mega_price}")

    # Создаем XML-дерево
    tree = ElementTree(yml_catalog)
    # Записываем XML в файл
    tree.write(f"{path}{filename}.xml", encoding="utf-8", xml_declaration=True)
    return f"{path}{filename}.xml"


def outlets(_dirr: str, shop_id: int, phone: str, brand: str, pid: str, shop_name: str) -> None:
    """
    Функция формирует для Мегамаркета информацию о точке
    обязательно каждый день должен быть файл с актуальной информацией
    :param _dirr: Директория в которой находится json файл
    :param shop_id: Айди кабинета
    :param phone: Телефон точки
    :param brand: Магазин
    :param pid: Обозначение точки
    :param shop_name: Наименование точки
    :return:
    """
    p = os.listdir(_dirr)
    e = [f for f in p if "outlets" in f]
    if e:
        os.remove(os.path.join(_dirr, e[0]))

    now = datetime.now()
    timezone = "+02:00"
    # Обязательные параметры для формирования json файла
    data = {
        "fileAttributes": {
            "merchantId": shop_id,
            "type": "outlets",
            "dateTime": f"{now.strftime("%Y-%m-%dT%H-%M-%S")}+03-00"
        },
        "outlets": [{
            "identification": {
                "id": pid,
                "name": shop_name,
            },
            "location": {
                "timezone": f"{timezone}",
                "address": {
                    "plain": "Театральная 30, Калининград, Калининградская обл.",
                    "postalCode": "236029"
                },
                "geo": {
                    "lat": "54.7173932",
                    "lon": "20.501255"
                },
                "directions": {
                    "metro": "",
                    "tripDescription": ""
                }
            },
            "label": {
                "caption": brand,
                "address": "Театральная 30, Калининград, Калининградская обл.",
                "imageUrl": "",
                "contacts": phone,
                "schedule": "Пн-Вс: 10:00 – 21:00"
            },
            "legalInfo": {
                "plain": ""
            },
            "roles": {
                "store": {
                    "operations": {
                        "packing": {
                            "schedule": {
                                "weekDayRules": {
                                    "monday": [10, 21],
                                    "tuesday": [10, 21],
                                    "wednesday": [10, 21],
                                    "thursday": [10, 21],
                                    "friday": [10, 22],
                                    "saturday": [10, 22],
                                    "sunday": [10, 21],
                                    "closed": [f"{now.year + 1}-01-01"]
                                }
                            },
                            "durationHours": 1
                        },
                        "handover": {
                            "schedule": {
                                "weekDayRules": {
                                    "monday": [10, 21],
                                    "tuesday": [10, 21],
                                    "wednesday": [10, 21],
                                    "thursday": [10, 21],
                                    "friday": [10, 22],
                                    "saturday": [10, 22],
                                    "sunday": [10, 21],
                                    "closed": [f"{now.year + 1}-01-01"]
                                }
                            }, "reservationPeriodDays": 2,
                            "paymentOptions": {
                                "prepayOnline": True,
                                "cash": True,
                                "bankCards": True
                            }
                        }
                    }
                }
            },
            "isActive": True
        }]
    }
    # Нейминг тоже важен, без этого мегамаркет не будет работать
    with open(os.path.join(_dirr, f"{shop_id}_outlets_{now.strftime("%Y-%m-%dT%H-%M-%S")}+03-00.json"), "w") as file:
        file.write(json.dumps(data))


def offer(_data, full=False) -> dict:
    """
    Функция формирования списка предложения
    Вызывается для двух Json файлов.
    Full - Это где перечислены все товары, остаток не учитывается
    Без Full формируются товарные предложения с реальным остатком.
    :param _data: Элемент offer из XML фида
    :param full: Для full файла/для diff файла
    :return:
    """
    _data = str(_data)
    available = re.findall(r'available="(true|false)"', _data)[0]
    if available == "true":
        _id = re.search(r'id="([^"]+)"', _data).group(1)
        _price = re.search(r"<price>(\d+)</price>", _data)
        if _price:
            if full:
                res = {
                    "offerId": _id,
                    "price": int(_price.group(1)),
                    "quantity": 0,
                }
            else:
                quantity = re.search(r"<count>([\d.]+)</count>", _data).group(1)
                res = {
                    "offerId": _id,
                    "price": int(_price.group(1)),
                    "quantity": int(quantity),
                }
            return res


def data_of_stocks(_dirr: str, shop_id: int, pid: str, route: str, prefix: str, full: bool):
    """
    Информация об остатках
    :param _dirr: директория для сохранения файла
    :param shop_id: айди кабинета
    :param pid: Обозначение точки
    :param route: путь до фида
    :param prefix: префикс diff/full
    :param full:
    :return:
    """
    p = os.listdir(_dirr)
    e = [f for f in p if f"_stocks_{prefix}_" in f]  # prefix full | diff
    if e:
        os.remove(os.path.join(_dirr, e[0]))

    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    timezone = "+03-00"

    with open(route, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), features="xml").find("offers").find_all("offer")

    data = {
        "fileAttributes": {
            "merchantId": shop_id,
            "type": "diff",
            "dateTime": f"{now}{timezone}"
        },
        "outlets": [{
            "outletId": pid,
            "offers": [offer(s, full=full) for s in soup if offer(s, full=full)]
        }]
    }
    with open(os.path.join(_dirr, f"{shop_id}_stocks_{prefix}_{now}{timezone}.json"), "w") as file:
        file.write(json.dumps(data))


def get_catalog_categories(url):
    """
    Парсинг категорий с xml файла
    :param url:
    :return:
    """
    req = requests.get(url).text.encode('latin-1').decode('utf-8')
    bs = BeautifulSoup(req, 'xml')
    _categories = bs.find("categories").find_all('category')
    res = {}
    for category in _categories:
        category = str(category)
        _id = re.search(r'id="(.*?)"', category).group(1)
        name = re.search(r'<category id="\d+" parentId="\d+">(.+?)</category>', category)
        name = name.group(1) if name else None
        if name:
            res[_id] = name
    return res


def megamarket_diff(content_url: str,
                    work_dirr: str,
                    warehouse: str,
                    tag: str,
                    tg: Telegram,
                    outlet_id: str,
                    shop_id: int,
                    pid: str,
                    file_name: str,
                    service_accounts: list[dict],
                    f: FilterItems = None,
                    df: pd.DataFrame = None,
                    partner_data: dict = None,
                    ):
    # создание номенклатуры
    nomenclature = create_nomeclature(
        url=content_url,
        warehouse_name=warehouse,
        df=df,
        parner_data=partner_data,
    )
    # установка цены
    nomenclature = setup_price(_items=nomenclature,
                               f=f,
                               service=service_accounts,
                               warehouse_name=warehouse)
    # создание xml файла
    path = xml_tree_builder(categories=get_catalog_categories(content_url),
                            _offers=nomenclature,
                            outlet_id=outlet_id,
                            filename=file_name,
                            path=work_dirr)
    # для регулярного запуска, только положительный остаток
    data_of_stocks(_dirr=work_dirr, shop_id=shop_id, pid=pid, route=path, prefix='diff', full=False)
    dirr = os.path.dirname(os.path.abspath(__file__))
    _route = os.path.join(dirr, f"json/{warehouse} message.json")
    # отчет в телегу
    text = f"*{warehouse} {tag}*\n"
    text += f"*Всего номенклатуры*: {len(nomenclature)}\n"
    text += f"*Товары в наличии*: {len([n for n in nomenclature if n.stock > 0])}\n"
    text += f"*Время обновления:* {datetime.today().strftime("%H:%M:%S")}\n"
    _path = make_order([n for n in nomenclature if n.basic_price], warehouse, tg, raw_name=warehouse)

    if f"{warehouse} message.json" not in os.listdir(os.path.join(dirr, 'json')):
        _archive = {"mes_id": tg.send_media(text=text, path=_path).message_id}
        with open(_route, "w") as f:
            json.dump(_archive, f)
    else:
        with open(_route) as f:
            _archive = json.load(f)
        tg.edit_mesg_media(mes_id=_archive.get("mes_id"), text=text, path=_path[0])


def data_soho(service) -> dict:
    """
    Табличка сохо из гугла
    :param service: список гугл-аккаунтов
    :return:
    """
    a = from_gsheet_to_df("Склад coxo + Марвел", "Смартфоны", "A:D",
                          "article", "item_name", "stock", "price", service=service)
    a["subgroup"] = "PDA"
    b = from_gsheet_to_df("Склад coxo + Марвел", "Экосистема", "A:D",
                          "article", "item_name", "stock", "cost", service=service)

    soho = pd.concat([a, b], ignore_index=True)
    result = {}
    for _, row in soho.iterrows():
        try:
            article = row.get('article')
            if article in ['#N/A', '#REF!', 'Артикул 1C']:
                continue

            stock = "".join(c for c in row.get('stock') if c.isdigit())
            stock = int(stock) if stock else 0
            price = row.get('price')
            if stock < 10 or price in ["", '#REF!', '#N/A', "0"]:
                continue
            result[article] = {}
            result[article]['stock'] = stock
            result[article]['price'] = float(price)
        except Exception as e:
            print(e)
            continue
    return result


class MarketplaceConfig:
    """
    Конфиг для передачи в Market и подключения к маркетплейсам
    """
    def __init__(
            self,
            oz_client_id: Optional[str] = None,
            oz_warehouse_id: Optional[int] = None,
            oz_key: str = Optional[None],
            ym_buisness_id: Optional[int] = None,
            ym_warehouse_id: Optional[int] = None,
            ym_token: Optional[str] = None,
    ):
        self.oz_client_id = oz_client_id
        self.oz_warehouse_id = oz_warehouse_id
        self.oz_key = oz_key

        self.ym_buisness_id = ym_buisness_id
        self.ym_campaign_id = ym_warehouse_id
        self.ym_token = ym_token


class Market:
    """
    Основной модуль для автоматизацц маркетплейса
    """
    def __init__(
            self,
            tg: Telegram,
            warehouse_name: [str] = None,
            content_url: Optional[str] = None,
            serv_accounts: Optional[list[dict]] = None,
            _filter: Optional[FilterItems] = None,
            config: Optional[MarketplaceConfig] = None,
            partner: Optional[dict] = None,  # для смешивания номенклатуры
            tag: Optional[str] = None,
            partner_table: Optional[pd.DataFrame] = None,  # для использования внешних таблиц
            ntf: bool = True,  # уведомления по заказам
    ):
        """

        :param tg: Объект телеграмма
        :param warehouse_name: Наименование склада
        :param content_url: Ссылка на контент с сайта
        :param serv_accounts: Гугл аккаунты
        :param _filter: Фильтр для товаров
        :param config: MarketplaceConfig
        :param partner: Партнерская таблица
        :param tag: Тэг для отчетности
        :param partner_table: Если используется внешняя таблица без локальных
        :param ntf: Уведомления в телеграм по новым заказам
        """
        self.name = warehouse_name
        self.content_url = content_url
        self.serv_accounts = serv_accounts
        self.tg = tg
        self.filter = _filter
        self.nomeclature: list[Nomenclature] = []
        self.config = config
        self.text = f"*{warehouse_name} {tag}*\n"
        self.partner_data = partner
        self.tag = tag
        self.partner_table = partner_table
        self.ntf = ntf

    def gen_nomenclature(self):
        print("перебор номенклатуры")
        self.nomeclature = create_nomeclature(
            warehouse_name=self.name,
            url=self.content_url,
            df=self.partner_table,
            parner_data=self.partner_data,
        )
        self.nomeclature = setup_price(
            warehouse_name=f"{self.name if not self.tag else f"{self.name} {self.tag}"}",
            _items=self.nomeclature,
            f=self.filter,
            service=self.serv_accounts,
        )

    def update_market(self):
        markets = []
        self.text += f"*Всего*: {len(self.nomeclature)}\n"
        if self.config.ym_buisness_id:
            print('Создание яндекса')
            ym = YandexMarket(
                token=self.config.ym_token,
                client_id=self.config.ym_buisness_id,
                campaign_id=self.config.ym_campaign_id,
                nomenclature=self.nomeclature
            )
            markets.append(ym)

        if self.config.oz_client_id:
            print('Создание Озон')
            oz = Ozon(
                client_id=self.config.oz_client_id,
                api_key=self.config.oz_key,
                warehouse_id=self.config.oz_warehouse_id,
                nomenclature=self.nomeclature
            )
            markets.append(oz)

        for market in markets:
            try:
                new = market.create_items()
                if new[-1]:
                    print("Определены новые товаы")
                    self.text += f"*Новых товаров {market.name}*: {new[-1]}\n"
                market.update_price()
                print("Цены установлены")
                market.update_stocks()
                print("Остатки обновлены")
                self.text += f"*Всего на {market.name}*: {len(market.market_items())}\n"
            except Exception as e:
                print(str(e))
                self.text += f'{market.name} не обновлен из-за ошибки: `{e}`\n'
                continue
            # if self.ntf:
            #     notificate(warehause_name=f"{self.name if not self.tag else f"{self.name} {self.tag}"}",
            #                token='1848981508:AAE9GJIxFuEQO4-vJSPbw-jr4nmT-QyV_gE',
            #                client=market,
            #                service=self.serv_accounts)
        self.text += f"*Товары в наличии*: {len([v for v in self.nomeclature if v.stock > 0])}\n"
        self.text += f"*Время обновления:* {datetime.today().strftime("%H:%M:%S")}\n"
        print(self.text)

    def order(self):
        print("создание отчета")
        dirr = os.path.dirname(os.path.realpath(__file__))
        # отправка отчета в телегу
        name = f"{self.name if not self.tag else f"{self.name} {self.tag}"}"
        order_name = f"{name} message.json"
        _route = os.path.join(dirr, f"json/{order_name}")
        _path = make_order([n for n in self.nomeclature if n.basic_price],
                           name,
                           self.tg,
                           raw_name=self.name,
                           )
        if order_name not in os.listdir(os.path.join(dirr, 'json')):
            _archive = {"mes_id": self.tg.send_media(text=self.text, path=_path).message_id}
            with open(_route, "w") as f:
                json.dump(_archive, f)
        else:
            with open(_route) as f:
                _archive = json.load(f)
            self.tg.edit_mesg_media(mes_id=_archive.get("mes_id"), text=self.text, path=_path[0])


def get_nomenclature(data):
    """
    Функция для полученяи инфы о проданной номенклатуре
    :param data:
    :return:
    """
    return Nomenclature(
        article=data.get("article"),
        barcode=data.get("barcode"),
        basic_price=data.get("basic_price"),
        category=data.get("category"),
        compensation=data.get("compensation"),
        delivery_price=data.get("delivery_price"),
        description=data.get("description"),
        group=data.get("group"),
        mega_category=data.get("mega_category"),
        mega_commission=data.get("mega_commission"),
        mega_price=data.get("mega_price"),
        name=data.get("name"),
        ozon_category=data.get("ozon_category"),
        ozon_commission=data.get("ozon_commission"),
        ozon_price=data.get("ozon_price"),
        pictures=data.get("pictures"),
        site_category_id=data.get("site_category_id"),
        stock=data.get("stock"),
        vendor=data.get("vendor"),
        warehouse=data.get("warehouse"),
        yandex_category=data.get("yandex_category"),
        yandex_commission=data.get("yandex_commission"),
        yandex_price=data.get("yandex_price")
    )


def update_order(rows: list, service: list[dict], warehause_name: str):
    """
    Функция для автоматического заполнения таблицы с отчетностью
    :param rows: Строки, для put в таблицу
    :param service: Гугл аккаунты
    :param warehause_name: Наименование склада
    :return:
    """
    # Подключение к гуглу
    _client = client_credentials(service_acc=service)
    _sheet = _client.open("Отчет по Маркетплейс").worksheet("Данные")
    _vals: list[Cell] = _sheet.range("A:A")
    # Создание/Загрузка архива
    dirr = os.path.dirname(os.path.abspath(__file__))
    _json = f"gs_{warehause_name}.json"
    __route = os.path.join(dirr, _json)
    if _json in os.listdir(dirr):
        with open(__route) as f:
            archive = json.load(f)
    else:
        archive = {}

    # Поиск строки с которой начнем заполнение
    static_row = None
    for v in _vals:
        if v.value == '':
            static_row = v.row
            break
    input_cells = []

    try:
        # заполняем каждую строку, если она уже в таблице, то обновляем по ней информацию
        for data in rows:
            order_num = data.get('order_num')
            row = static_row
            if data.get("edit"):
                for k, v in archive.items():
                    if order_num in v:
                        row = k
            else:
                static_row += 1
            archive[row] = []
            archive[row].append(order_num)
            input_cells.extend([
                Cell(row=row, col=1, value=data.get('date')),  # Дата заказа
                Cell(row=row, col=3, value=order_num),  # Номер заказа
                Cell(row=row, col=4, value=data.get('brand')),  # Бренд магазина
                Cell(row=row, col=5, value=data.get('name')),  # Наименование товара
                Cell(row=row, col=6, value=data.get('quantity')),  # Количество
                Cell(row=row, col=7, value=data.get('revenue')),  # Выручка
                Cell(row=row, col=8, value=data.get('cost')),  # Закуп
                Cell(row=row, col=9, value=data.get('compensation')),  # Компенсация
                Cell(row=row, col=13, value=data.get('commission')),  # Комиссия
                Cell(row=row, col=14, value=data.get('delivery_price')),  # Стоимость доставки
                Cell(row=row, col=18, value=data.get('storage')),  # Склад продажи
                Cell(row=row, col=19, value=data.get('market')),  # Маркетплейс наименование
                Cell(row=row, col=21, value=data.get('done')),  # Выполнен
                Cell(row=row, col=22, value=data.get('cancel')),  # Отменен
            ])
            # запись в таблицу
            if input_cells:
                _sheet.update_cells(input_cells)
    except Exception as e:
        raise e
    finally:
        with open(__route, "w") as f:
            json.dump(archive, f)


def notificate(warehouse_name: str, token: str, client: YandexMarket | Ozon,
               # service: list[dict]
               ):
    """
    Функция для уведомления по новым заказам в телеграмме
    """
    dirr = os.path.dirname(os.path.abspath(__file__))
    tg = Telegram(token=token, chat_id=-1002065287421)
    # загрузка информации о номенклатуре
    # with (open(os.path.join(dirr, f"{warehause_name}.json")) as file):
    #     nom_info: dict = json.load(file)

    # Загрузка/Создание архива заказов
    _json = f"{client.name}_orders_{warehouse_name}.json"
    __route = os.path.join(dirr, f"json/{_json}")
    if _json in os.listdir(os.path.join(dirr, 'json')):
        with open(__route) as f:
            archive = json.load(f)
    else:
        archive = {}
    # получение списка заказов
    _orders = client.orders()
    base_url = "https://seller.ozon.ru/app/postings/fbs?tab=all&postingDetails=" if isinstance(client, Ozon) else \
        f"https://partner.market.yandex.ru/shop/{client.campaign_id}/orders/"
    # complite = [OrderStatusType.DELIVERED, PostingStatusType.delivered]
    # canseled = [OrderStatusType.CANCELLED,
    #             OrderStatusType.RETURNED,
    #             OrderStatusType.PARTIALLY_RETURNED,
    #             PostingStatusType.cancelled,
    #             PostingStatusType.cancelled_from_split_pending,
    #             PostingStatusType]
    try:
        for _ord in _orders:
            time.sleep(0.5)
            # try:
            date = _ord.creation_date.replace("T", " ").replace("Z", "")[:10]
            # отсечная черта, чтобы не спамить тем, что уже отправлено
            date = datetime.strptime(date, "%d-%m-%Y").date() if isinstance(client, YandexMarket) else \
                datetime.strptime(date, "%Y-%m-%d").date()
            if date >= datetime.strptime("30-07-2024", "%d-%m-%Y").date():
                print(_ord.id)
                title = (f"-----{client.name}-----\n"
                         f"{warehouse_name}\n")
                if str(_ord.id) not in archive:
                    # отправляем уведомление в телегу и записываем заказ в архив
                    mes = tg.send_telegram(text=f"{title}{str(_ord)}", link=f"{base_url}{_ord.id}")
                    archive[str(_ord.id)] = {}
                    archive[str(_ord.id)]["data"] = to_json(_ord)
                    archive[str(_ord.id)]["mes_id"] = mes.message_id
                    # проверяем статус, для установки отмены/выполнения статуса заказа
                    # for row in old.get("rows"):
                    #     if old["data"]["status"] != _ord.status:
                    #         row["done"] = True if _ord.status in complite else False
                    #         row["cancel"] = True if _ord.status in canseled else False
                    #         row["edit"] = True
                    #     archive[str(_ord.id)]["rows"].append(row)
                else:
                    # сравниваем архивный заказ с новыми данными, если изменения есть, вносим их в телеграмм
                    old = archive.get(str(_ord.id))
                    raw_ord = to_json(_ord)
                    diff_keys = [key for key in raw_ord if raw_ord.get(key) != old['data'].get(key)]
                    if any(diff_keys):
                        tg.edit_message(text=f"{title}{str(_ord)}", message_id=old.get("mes_id"),
                                        link=f"{base_url}{_ord.id}")
                        archive[str(_ord.id)]["data"] = raw_ord
                        archive[str(_ord.id)]["mes_id"] = old.get("mes_id")
            # except Exception:
            #     continue
            # Передача информации о заказе, который мы записываем в отчетную гугл таблицу
            # archive[str(_ord.id)]["rows"] = []
            # nmn = [get_nomenclature(nom_info.get(a.offer_id)) for a in _ord.items if nom_info.get(a.offer_id)]
            # данные по заказу для отчетности
            # for p in nmn:
            #     row = dict(
            #         date=str(date).replace("-", "."),
            #         order_num=_ord.id,
            #         brand="Sony" if warehause_name == "Склад Sony" else "Mi",
            #         name=p.name,
            #         quantity=1,
            #         revenue=p.ozon_price if isinstance(client, Ozon) else p.yandex_price,
            #         cost=p.basic_price,
            #         compensation=p.compensation if p.compensation else 0,
            #         commission=p.ozon_comission / 100 if isinstance(client, Ozon) else p.yandex_comission / 100,
            #         delivery_price=p.delivery_price / len(nmn),
            #         storage=p.warehouse,
            #         market="OZON" if isinstance(client, Ozon) else "Яндекс маркет",
            #         done=True if _ord.status in complite else False,
            #         cancel=True if _ord.status in canseled else False,
            #         edit=False,
            #     )
            #     archive[str(_ord.id)]["rows"].append(row)
        # чтобы не растягивать архив заказов, стираем те, которых уже нет в ответе маркета
        keys = [str(o.id) for o in _orders]
        for key in archive.copy():
            if key not in keys:
                archive.pop(key)
        print(len(archive))
        with open(__route, "w") as f:
            json.dump(archive, f)
        # передача информации для записи в таблицу
        # rows = [row for val in archive.values() for row in val.get("rows")]
        # update_order(rows, service, warehause_name)

    except Exception as e:
        print(e)
        tg.send_telegram(chat_id=-1002196776398, text=f"{client.name}\n{warehouse_name}\nОшибка:```{str(e)}```")
        raise e


def nom_ids():
    """
    Функция, для получения уникальных идентификаторов номенклатуры в эску,
    без них не получится соединить цены с номенклатурой
    :return:
    """
    # dirr = os.path.abspath(os.path.dirname(__file__))
    # путь всегда один и тот же, поэтому прописан руками
    remote_dir = "/home/odinass/data"
    name = 'Nomenklatura s identifikatorami (XLSX).xlsx'
    path = os.path.join(remote_dir, f'{name}')
    _ids = pd.read_excel(path)
    _ids = _ids.rename(columns={"Артикул ": "article",
                                "Уникальный идентификатор": "uid",
                                "Наименование": "item_name"})
    return {r.article: r.uid for _, r in _ids.iterrows()}


class PriceTypes:
    """
    Виды цен в номенклатуре
    """
    yandex_coxo: str = "Цена Я.Маркет КО - СОХО"
    main: str = "Основная цена покупки"
    ozon_rf: str = "Цена Ozon - РФ"
    mega_ko: str = "Цена Мегамарткет КО"
    mega_rf: str = "Цена Мегамарткет РФ"
    yandex_ko: str = "Цена Я.Маркет КО"
    yandex_rf: str = "Цена Я.Маркет РФ"
    ozon_ko: str = "Цена Ozon"
    ozon_coxo: str = "Цена Ozon - СОХО"


def price_for_onec(
        df: pd.DataFrame,
        # data_file_name: str,
        output_file_name: str,
        price_type: str,
):
    """
    Функция для формирования видов цен в номенклатуру
    :param df: Таблица с текущими ценами (из функции Make_order)
    :param output_file_name: Выходное наименование файла
    :param price_type: Тип цены
    :return:
    """
    # Где ключ - Вид цены, значение - ее идентификатор в эске
    price_types = {"Цена Я.Маркет КО - СОХО": "6e01a248-531e-11ef-8881-001dd8bb1ea5",
                   "Основная цена покупки": "440bbbe6-038d-11e0-9731-001e5848397d",
                   "Цена Ozon - РФ": "644aac48-531e-11ef-8881-001dd8bb1ea5",
                   "Цена Мегамарткет КО": "1f729305-baa3-11ee-8877-001dd8bb1ea5",
                   "Цена Мегамарткет РФ": "2a39ec46-b39c-11ee-8876-001dd8bb1ea5",
                   "Цена Я.Маркет КО": "01a18af3-10fa-11ee-8870-001dd8bb1ea5",
                   "Цена Я.Маркет РФ": "e0011ce4-10f9-11ee-8870-001dd8bb1ea5",
                   "Цена Ozon": "cd65a9b5-100c-11ee-8870-001dd8bb1ea5",
                   "Цена Ozon - СОХО": "31b1e96d-531f-11ef-8881-001dd8bb1ea5"}
    # Определяем столбец df, из которого берем значение цены
    if price_type in ["Цена Ozon - РФ", "Цена Ozon", "Цена Ozon - СОХО"]:
        col = "Цена Озон"
    elif price_type in ["Цена Я.Маркет КО - СОХО", "Цена Я.Маркет КО", "Цена Я.Маркет РФ"]:
        col = "Цена Яндекс"
    else:
        col = "Цена Мега"
    # идентификаторы номенклатуры
    ids = nom_ids()
    dirr = os.path.abspath(os.path.dirname(__file__))
    # path = os.path.join(dirr, f"{data_file_name}.xlsx")
    # df = pd.read_excel(path)
    data = {
        'A': [''],  # indexes
        'B': [''],  # articles
        'C': [''],  # uids
        'D': [''],  # uids_idf
        'E': [''],  # names
        'F': ['Старая цена'],  # old
        'G': ['Изменение'],  # change
        'H': ['%'],  # percent
        'I': ['Цена'],  # price
        'J': ['Ед. изм.'],  # quan
        'K': ['Уникальный идентификатор (Единица измерения)'],  # uuids
    }
    idx = 1
    # генерим данные по номенклатуре для установки цен
    for i, row in df.iterrows():
        val = row[col]
        article = row['Артикул']
        _id = ids.get(article)
        if pd.isnull(val) or not _id:
            continue
        data['A'].append(str(idx))
        data['B'].append(article)
        data['C'].append(_id)
        data['D'].append('00000000-0000-0000-0000-000000000000')
        data['E'].append(row['Наименование'])
        data['F'].append('')
        data['G'].append('')
        data['H'].append('0')
        data['I'].append(val)
        data['J'].append('ШТ')
        data['K'].append('00000000-0000-0000-0000-000000000000')
        idx += 1
    # Начинаем формировать таблицу под требования эски
    df = pd.DataFrame(data)
    path = os.path.join(dirr, f"xls/{output_file_name}.xls")
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        # Получаем доступ к объекту workbook и worksheet
        workbook: xlsxwriter.Workbook = writer.book
        sheet = workbook.add_worksheet('Лист1')
        data = [
            ['Уникальный идентификатор',
             'Вид цены',
             'Номер колонки "Старая цена"',
             'Номер колонки "Процент изменения"',
             'Номер колонки "Цена"',
             'Номер колонки "Единица измерения"',
             'Номер колонки "Уникальный идентификатор"'],
            [price_types[price_type], price_type, 6, 8, 9, 10, 11, ]

        ]
        for row_num, row_data in enumerate(data):
            sheet.write_row(row_num, 0, row_data)

        df.to_excel(writer, sheet_name='TDSheet', index=False)
        worksheet: Worksheet = writer.sheets['TDSheet']
        # Объединяем ячейки (например, A1:A2)
        worksheet.merge_range("A1:A2", '№')
        worksheet.merge_range("B1:B2", 'Артикул')
        worksheet.merge_range("C1:C2", "Уникальный идентификатор (Номенклатура)")
        worksheet.merge_range("D1:D2", "Уникальный идентификатор (Характеристика)")
        worksheet.merge_range("E1:E2", "Товар")
        worksheet.merge_range("F1:K1", price_type)
    return path


def main_price(s):
    """
    Функция для получения информации, на какую номенклатуру установить статичную цену
    (Использовалось, для того чтобы слить определенные позиции побыстрее и продажи в минус)
    :param s: гугл аккаунты
    :return:
    """
    sheet = client_credentials(s).open("Комиссии Маркетплейсов").worksheet("Принудительная розница")
    articles = sheet.range("A:A")
    price: list[Cell] = sheet.range("C:C")
    res = {}
    for idx, cell in enumerate(articles):
        if cell.value == '':
            break
        if cell.value == 'Артикул':
            continue
        res[cell.value] = float(price[idx].value)
    return res
