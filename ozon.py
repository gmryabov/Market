"""
Все объекты были взяты из оф. документации озон
https://docs.ozon.ru/api/seller/#operation
"""


import json
import os
import pprint
from datetime import timedelta, datetime
from langdetect import detect
import pandas as pd
import random
from main import ozon_types
import requests
from typing import Optional, Any
from main.custom_classes import Nomenclature


class Category:
    def __init__(self, data):
        self.description_category_id = data.get("description_category_id")
        self.category_name = data.get("category_name")
        self.children = [Category(c) for c in data.get("children")]
        self.disabled = data.get("disabled")
        self.type_id = data.get("type_id")
        self.type_name = data.get("type_name")


class OfferItem:
    def __init__(self, offer_id: str, product_id: int):
        self.offer_id = offer_id
        self.product_id = product_id

    def __str__(self):
        return f"{self.offer_id}: {self.product_id}"


class OffersPaginationResponse:
    def __init__(self, _result: dict):
        self.items = [OfferItem(o.get("offer_id"), o.get("product_id")) for o in _result.get("items")]
        self.last_id = _result.get("last_id")
        self.total = _result.get("total")


class OzonResponse:
    def __init__(self, _result: dict):
        self.code: int = _result.get("code")
        self.message: str = _result.get("message")
        self.details: list = _result.get("details")
        self.result: dict = _result.get("result")


class FirstMile:
    def __init__(self, _result: dict):
        self.dropoff_point_id: str = _result.get("dropoff_point_id")
        self.dropoff_timeslot_id: int = _result.get("dropoff_timeslot_id")
        self.first_mile_is_changing: bool = _result.get("first_mile_is_changing")
        self.first_mile_type: str = _result.get("first_mile_type")


class Warehouse:
    def __init__(self, _result: dict):
        self.warehouse_id: int = _result.get("warehouse_id")
        self.name: str = _result.get("name")
        self.is_rfbs: bool = _result.get("is_rfbs")
        self.is_able_to_set_price: bool = _result.get("is_able_to_set_price")
        self.first_mile_type = FirstMile(_result.get("first_mile_type"))
        self.is_kgt: bool = _result.get("is_kgt")
        self.can_print_act_in_advance: bool = _result.get("can_print_act_in_advance")
        self.min_working_days: int = _result.get("min_working_days")
        self.is_karantin: bool = _result.get("is_karantin")
        self.has_postings_limit: bool = _result.get("has_postings_limit")
        self.postings_limit: int = _result.get("postings_limit")
        self.working_days: list[int] = _result.get("working_days")
        self.min_postings_limit: int = _result.get("min_postings_limit")
        self.is_timetable_editable: bool = _result.get("is_timetable_editable")
        self.status: str = _result.get("status")
        self.is_economy: bool = _result.get("is_economy")


class ItemPdfList:
    def __init__(self, index: int, name: str, src_url: str):
        self.index = index
        self.name = name
        self.src_url = src_url


class AttributeValues:
    def __init__(self, dictionary_value_id: int, value: str):
        self.dictionary_value_id = dictionary_value_id
        self.value = value


class ItemAttributes:
    def __init__(self, complex_id: int, _id: int, values: AttributeValues):
        self.complex_id = complex_id
        self.id = _id
        self.values = values


class DataCreateItem:
    def __init__(self,
                 offer_id: str,
                 description_category_id: int,
                 price: str,
                 name: str,
                 barcode: str,
                 weight: int,
                 width: int,
                 height: int,
                 depth: int,
                 currency_code: ozon_types.CurrencyType | str,
                 dimension_unit: ozon_types.DimensionUnitType | str,
                 weight_unit: ozon_types.WeightUnitType | str,
                 vat: ozon_types.ItemVatType | int | float,
                 images: Optional[list[str]] = None,
                 primary_image: Optional[str] = None,
                 service_type: Optional[ozon_types.ItemServiceType] = None,
                 image_group_id: Optional[str] = None,
                 attributes: Optional[list[ItemAttributes]] = None,
                 geo_names: Optional[list[str]] = None,
                 premium_price: Optional[str] = None,
                 complex_attributes: Optional[list] = None,
                 color_image: Optional[str] = None,
                 images360: Optional[list[str]] = None,
                 old_price: Optional[str] = None,
                 pdf_list: Optional[ItemPdfList] | list = None,
                 ):
        self.offer_id = offer_id
        self.description_category_id = description_category_id
        self.price = price
        self.name = name
        self.barcode = barcode
        self.weight = weight
        self.width = width
        self.height = height
        self.depth = depth
        self.currency_code = currency_code
        self.dimension_unit = dimension_unit
        self.weight_unit = weight_unit
        self.vat = vat
        self.images = images
        self.primary_image = primary_image
        self.service_type = service_type
        self.image_group_id = image_group_id
        self.attributes = attributes
        self.geo_names = geo_names
        self.premium_price = premium_price
        self.complex_attributes = complex_attributes
        self.color_image = color_image
        self.images360 = images360
        self.old_price = old_price
        self.pdf_list = pdf_list


class ItemOzonStocks:
    def __init__(self, _discounted_stocks: dict):
        self.coming: int = _discounted_stocks.get("coming")
        self.present: int = _discounted_stocks.get("present")
        self.reserved: int = _discounted_stocks.get("reserved")


class IndexData:
    def __init__(self, _index_data: dict):
        if _index_data is not None:
            self.minimal_price: str = _index_data.get("minimal_price")
            self.minimal_price_currency: str = _index_data.get("minimal_price_currency")
            self.price_index_value: float = _index_data.get("price_index_value")
        else:
            self.minimal_price = None
            self.minimal_price_currency = None
            self.price_index_value = None


class PriceIndexes:
    def __init__(self, _price_indexes: dict):
        self.external_index_data: IndexData = IndexData(_price_indexes.get("external_index_data")) \
            if "external_index_data" in _price_indexes else None
        self.ozon_index_data: IndexData = IndexData(_price_indexes.get("ozon_index_data")) \
            if "ozon_index_data" in _price_indexes else None
        self.price_index: ozon_types.PriceIndexType = _price_indexes.get("price_index") \
            if "price_index" in _price_indexes else None
        self.self_marketplaces_index_data = IndexData(_price_indexes.get("self_marketplaces_index_data")) \
            if "self_marketplaces_index_data" in _price_indexes else None


class ItemOzonErrors:
    def __init__(self, _errors: dict):
        self.code: str = _errors.get("code")
        self.state: str = _errors.get("state")
        self.level: str = _errors.get("level")
        self.description: str = _errors.get("description")
        self.field: str = _errors.get("field")
        self.attribute_id: int = _errors.get("attribute_id")
        self.attribute_name: str = _errors.get("attribute_name")
        self.optional_description_elements: object = _errors.get("optional_description_elements")


class ItemOzonStatus:
    def __init__(self, _status: dict):
        self.state: str = _status.get("state")
        self.state_failed: str = _status.get("state_failed")
        self.moderate_status: str = _status.get("moderate_status")
        self.decline_reasons: list[str] = _status.get("decline_reasons")
        self.validation_state: str = _status.get("validation_state")
        self.state_name: str = _status.get("state_name")
        self.state_description: str = _status.get("state_description")
        self.is_failed: bool = _status.get("is_failed")
        self.is_created: bool = _status.get("is_created")
        self.state_tooltip: str = _status.get("state_tooltip")
        self.item_errors: list[ItemOzonErrors] = [ItemOzonErrors(er) for er in _status.get("item_errors")]
        self.state_updated_at: str = _status.get("state_updated_at")


class ItemOzonSources:
    def __init__(self, _sources: dict):
        self.is_enabled: bool = _sources.get("is_enabled")
        self.sku: str = _sources.get("sku")
        self.source: str = _sources.get("source")


class VisibilityDetails:
    def __init__(self, _visibility_details: dict):
        self.active_product: bool = _visibility_details.get("active_product")
        self.has_price: bool = _visibility_details.get("has_price")
        self.has_stock: bool = _visibility_details.get("has_stock")
        self.reasons: object = _visibility_details.get("reasons")


class DataOzonItem:
    def __init__(self, _data: dict):
        self.is_archived: bool = _data.get("is_archived")
        self.is_autoarchived: bool = _data.get("is_autoarchived")
        self.barcode: str = _data.get("barcode")
        self.barcodes: list[str] = _data.get("barcodes")
        self.buybox_price: str = _data.get("buybox_price")
        self.category_id: int = _data.get("category_id")
        self.description_category_id: int = _data.get("description_category_id")
        self.type_id: int = _data.get("type_id")
        self.color_image: str = _data.get("color_image")
        self.created_at: str = _data.get("created_at")
        self.sku: str = _data.get("sku")
        # self.fbo_sku: str = _data.get("fbo_sku") # old
        # self.fbs_sku: str = _data.get("fbs_sku") # old
        self.id: int = _data.get("id")
        self.images: list[str] = _data.get("images")
        self.primary_image: str = _data.get("primary_image")
        self.images_360: list[str] = _data.get("images360")
        self.has_discounted_item: bool = _data.get("has_discounted_item")
        self.is_discounted: bool = _data.get("is_discounted")
        self.discounted_stocks = ItemOzonStocks(_data.get("discounted_stocks")) \
            if "discounted_stocks" in _data else None
        self.is_kgt: bool = _data.get("is_kgt")
        self.currency_code: ozon_types.CurrencyType = _data.get("currency_code")
        self.marketing_price: str = _data.get("marketing_price")
        self.min_ozon_price: str = _data.get("min_ozon_price")
        self.min_price: str = _data.get("min_price")
        self.name: str = _data.get("name")
        self.offer_id: str = _data.get("offer_id")
        self.old_price: str = _data.get("old_price")
        self.premium_price: str = _data.get("premium_price")
        self.price: str = _data.get("price")
        self.price_indexes: PriceIndexes = PriceIndexes(_data.get("price_indexes"))
        self.recommended_price: str = _data.get("recommended_price")
        self.sources = [ItemOzonSources(o) for o in _data.get("sources") if "sources" in _data]
        self.stocks = ItemOzonStocks(_data.get("stocks")) if "stocks" in _data else None
        self.updated_at: str = _data.get("updated_at")
        self.vat: ozon_types.ItemVatType = _data.get("vat")
        self.visible: bool = _data.get("visible")


class UpdatePriceItem:
    def __init__(
            self,
            price: str,
            offer_id: str,
            min_price: Optional[str] = None,
            old_price: Optional[str] = None,
            product_id: Optional[int] = None,
            auto_action_enabled: Optional[ozon_types.EnabledType] = None,
            currency_code: Optional[ozon_types.CurrencyType] = None,
            price_strategy_enabled: Optional[ozon_types.EnabledType] = None,
    ):
        self.auto_action_enabled = auto_action_enabled
        self.currency_code = currency_code
        self.min_price = min_price
        self.offer_id = offer_id
        self.old_price = old_price
        self.price = price
        self.price_strategy_enabled = price_strategy_enabled
        self.product_id = product_id


class UpdateStockItem:
    def __init__(
            self,
            offer_id: str,
            stock: int,
            warehouse_id: int,
            product_id: Optional[int] = None,
    ):
        self.offer_id = offer_id
        self.stock = stock
        self.warehouse_id = warehouse_id
        self.product_id = product_id


class ErrorDesc:
    def __init__(self, data: dict):
        self.code: str = data.get("code")
        self.message: str = data.get("message")


class StocksResponse:
    def __init__(self, data: dict):
        self.errors: list[ErrorDesc] = [ErrorDesc(er) for er in data.get("errors")]
        self.offer_id: str = data.get("offer_id")
        self.product_id: int = data.get("product_id")
        self.updated: bool = data.get("updated")
        self.warehouse_id: int = data.get("warehouse_id")


class LastChangedStatusDate:
    def __init__(self, _from: str, to: str):
        self._from = _from
        self._to = to


class FilterOrders:
    def __init__(self,
                 since: str,
                 to: str,
                 delivery_method_id: Optional[int] = None,
                 order_id: Optional[int] = None,
                 provider_id: Optional[list[int]] = None,
                 status: Optional[ozon_types.PostingStatusType | str] = None,
                 warehouse_id: Optional[int] = None,
                 last_changed_status_date: Optional[LastChangedStatusDate] = None,
                 ):
        self.delivery_method_id = delivery_method_id
        self.order_id = order_id
        self.provider_id = provider_id
        self.since = since
        self.to = to
        self.status = status
        self.warehouse_id = warehouse_id
        self.last_changed_status_date = last_changed_status_date


class MoreDataWith:
    def __init__(self,
                 analytics_data: Optional[bool] = False,
                 barcodes: Optional[bool] = False,
                 financial_data: Optional[bool] = False,
                 translit: Optional[bool] = False):
        self.analytics_data = analytics_data
        self.barcodes = barcodes
        self.financial_data = financial_data
        self.translit = translit


class PostingGetter:
    def __init__(self,
                 _dir: Optional[ozon_types.SortDirectionType | str],
                 _filter: FilterOrders,
                 limit: int,
                 offset: int,
                 _with: Optional[MoreDataWith] = None):
        self.dir = _dir
        self.filter = _filter
        self.limit = limit
        self.offset = offset


class PostingBarcodes:
    def __init__(self, data: dict):
        self.lower_barcode: str = data.get("lower_barcode")
        self.upper_barcode: str = data.get("upper_barcode")


class PostingAnalyticsData:
    def __init__(self, data: dict):
        self.city: str = data.get("city")
        self.delivery_date_begin: str = data.get("delivery_date_begin")
        self.delivery_date_end: str = data.get("delivery_date_end")
        self.delivery_type: str = data.get("delivery_type")
        self.is_legal: bool = data.get("is_legal")
        self.is_premium: bool = data.get("is_premium")
        self.payment_type_group_name: ozon_types.PaymentType = data.get("payment_type_group_name")
        self.region: str = data.get("region")
        self.tpl_provider: str = data.get("tpl_provider")
        self.tpl_provider_id: int = data.get("tpl_provider_id")
        self.warehouse: str = data.get("warehouse")
        self.warehouse_id: int = data.get("warehouse_id")


class PostingCancellationReason:
    def __init__(self, data: dict):
        self.affect_cancellation_rating: bool = data.get("affect_cancellation_rating")
        self.cancel_reason: str = data.get("cancel_reason")
        self.cancel_reason_id: int = data.get("cancel_reason_id")
        self.cancellation_initiator: ozon_types.CancellationInitiatorType = data.get("cancellation_initiator")
        self.cancellation_type: ozon_types.CancellationType = data.get("cancellation_type")
        self.cancelled_after_ship: bool = data.get("cancelled_after_ship")


class Address:
    def __init__(self, data: dict):
        self.address_tail: str = data.get("address_tail")  # адрес в текстовом формате
        self.city: str = data.get("city")
        self.comment: str = data.get("comment")
        self.country: str = data.get("country")
        self.district: str = data.get("district")
        self.latitude: float = data.get("latitude")
        self.longitude: float = data.get("longitude")
        self.provider_pvz_code: str = data.get("provider_pvz_code")
        self.pvz_code: int = data.get("pvz_code")
        self.region: str = data.get("region")
        self.zip_code: str = data.get("zip_code")  # Почтовый индекс получателя


class Customer:
    def __init__(self, data: dict):
        self.address = Address(data.get("address"))
        self.customer_id: int = data.get("customer_id")
        self.name: str = data.get("name")
        self.phone: str = data.get("phone")


class DeliveryMethod:
    def __init__(self, data: dict):
        self.id: int = data.get("id")
        self.name: str = data.get("name")
        self.tpl_provider: str = data.get("tpl_provider")
        self.tpl_provider_id: int = data.get("tpl_provider_id")
        self.warehouse: str = data.get("warehouse")
        self.warehouse_id: int = data.get("warehouse_id")


class PickingInfo:
    def __init__(self, data: dict):
        self.amount: float = data.get("amount")
        self.moment: str = data.get("moment")
        self.tag: str = data.get("tag")


class PostingFinancialProduct:
    def __init__(self, data: dict):
        self.actions: list[str] = data.get("actions")
        self.currency_code: ozon_types.CurrencyType = data.get("currency_code")
        self.commission_amount: float = data.get("commission_amount")
        self.commission_percent: int = data.get("commission_percent")
        self.commissions_currency_code: str = data.get("commissions_currency_code")
        self.payout: float = data.get("payout")  # выбплата селлеру
        self.picking = PickingInfo(data.get("picking")) if "picking" in data else None
        self.price: str = data.get("price")
        self.product_id: int = data.get("product_id")
        self.quantity: int = data.get("quantity")
        self.total_discount_percent: float = data.get("total_discount_percent")
        self.total_discount_value: float = data.get("total_discount_value")


class FinancialData:
    """Данные о стоимости товара, размере скидки, выплате и комиссии."""

    def __init__(self, data: dict):
        self.cluster_from: str = data.get("cluster_from")
        self.cluster_to: str = data.get("cluster_to")
        self.products: list[PostingFinancialProduct] = [PostingFinancialProduct(p) for p in data.get("products")]


class PostingRequirements:
    """
    Cписок продуктов, для которых нужно передать
    страну-изготовителя, номер грузовой таможенной
    декларации (ГТД), регистрационный номер партии
    товара (РНПТ) или маркировку «Честный ЗНАК»,
    чтобы перевести отправление в следующий статус.
    """

    def __init__(self, data: dict):
        self.products_requiring_gtd: list[str] = data.get("products_requiring_gtd")
        self.products_requiring_country: list[str] = data.get("products_requiring_country")
        self.products_requiring_mandatory_mark: list[str] = data.get("products_requiring_mandatory_mark")
        self.products_requiring_jw_uin: list[str] = data.get("products_requiring_jw_uin")
        self.products_requiring_rnpt: list[str] = data.get("products_requiring_rnpt")


class AddresSee:
    def __init__(self, data_address: dict):
        self.name: str = data_address.get("name")
        self.city: str = data_address.get("city")


class PostingProduct:
    def __init__(self, data: dict):
        self.mandatory_mark: list[str] = data.get("mandatory_mark")
        self.name: str = data.get("name")
        self.offer_id: str = data.get("offer_id")
        self.price: str = data.get("price")
        self.quantity: int = data.get("quantity")
        self.sku: int = data.get("sku")
        self.currency_code: ozon_types.CurrencyType = data.get("currency_code")


class OzonOrder:
    def __init__(self, data: dict):
        self.addressee = AddresSee(data.get("addressee")) if data.get("addressee") else None
        self.analytics_data = PostingAnalyticsData(data.get("analytics_data")) if data.get("analytics_data") else None
        self.barcodes = PostingBarcodes(data.get("barcodes")) if data.get("barcodes") else None
        self.cancellation = PostingCancellationReason(data.get("cancellation")) if data.get("cancellation") else None
        self.customer = Customer(data.get("customer")) if data.get("customer") else None
        self.delivering_date: str = data.get("delivering_date")
        self.delivery_method = DeliveryMethod(data.get("delivery_method")) if data.get("delivery_method") else None
        self.financial_data = FinancialData(data.get("financial_data")) if data.get("financial_data") else None
        self.creation_date: str = data.get("in_process_at")
        self.is_express: bool = data.get("is_express")
        self.is_multibox: bool = data.get("is_multibox")
        self.multi_box_qty: int = data.get("multi_box_qty")
        self.order_id: int = data.get("order_id")
        self.order_number: str = data.get("order_number")
        self.parent_posting_number: str = data.get("parent_posting_number")
        self.id: str = data.get("posting_number")
        self.items: list[PostingProduct] = [PostingProduct(p) for p in data.get("products") if data.get("products")]
        self.prr_option: ozon_types.PrrOptionType = data.get("prr_option")
        self.requirements = PostingRequirements(data.get("requirements")) if data.get("requirements") else None
        self.shipment_date: str = data.get("shipment_date")
        self.status: ozon_types.PostingStatusType = data.get("status")
        self.substatus: ozon_types.PostingStatusType = data.get("substatus")
        self.tpl_integration_type: ozon_types.TplIntegrationType = data.get("tpl_integration_type")
        self.tracking_number: str = data.get("tracking_number")

    def __str__(self):
        text = f"*Номер заказа:* `{self.id}`\n"
        text += f"*Дата:* {self.creation_date.replace("T", " ").replace("Z", "")}\n"
        true_status = {"awaiting_registration": "⏳ Ожидает регистрации",
                       "acceptance_in_progress": "📦 Идёт приёмка",
                       "awaiting_approve": "⏳ Ожидает подтверждения",
                       "awaiting_packaging": "⏳ Ожидает упаковки",
                       "awaiting_deliver": "⏳ Ожидает отгрузки",
                       "awaiting_verification": "⚡️ Создано",
                       "arbitration": "👩‍⚖️ Арбитраж",
                       "client_arbitration": "⏳ Клиентский арбитраж доставки",
                       "cancelled_from_split_pending": "🚫 Отменён из-за разделения отправления",
                       "delivering": "🚚 Доставляется",
                       "driver_pickup": "🚚 У водителя",
                       "delivered": "✅ Доставлено",
                       "cancelled": "🚫 Отменено",
                       "not_accepted": "🚫 Не принят на сортировочном центре",
                       "sent_by_seller": "🚚 Отправлено продавцом", }
        text += f"*Статус:* {true_status.get(self.status)}\n"
        text += f'*Состав заказа:* \n`{'`\n`'.join([p.name for p in self.items])}`\n'
        text += f"*Сумма заказа:* {sum([float(p.price) for p in self.items])}\n"
        text += f"*Способ доставки:* {self.delivery_method.name}\n"
        text += f"*Склад:* {self.delivery_method.warehouse}"
        if self.customer:
            text += f"\n*Клиент:* {self.customer.name}"
            if self.customer.address:
                text += f"\n*Комментарий:* {self.customer.address.comment}"
                text += f"\n*Адрес:* {self.customer.address.address_tail}"
        return text


class PostingResponsePadding:
    def __init__(self, data: dict):
        self.has_next: bool = data.get("has_next")
        self.postings: list[OzonOrder] = [OzonOrder(pos) for pos in data.get("postings") if pos is not None]


class CreateItemInfo:
    def __init__(self, data: dict):
        self.offer_id: str = data.get("offer_id")
        self.product_id: int = data.get("product_id")
        self.status: ozon_types.CreateStatusType = data.get("status")


class Attributies:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.info = data.get("info")
        self.picture = data.get("picture")
        self.value = data.get("value")


class CreateItemResponse:
    def __init__(self, data: dict):
        self.total: int = data.get("total")
        self.items: list[CreateItemInfo] = [CreateItemInfo(t) for t in data.get("items")]


class ItemInfo:
    def __init__(self, x: str):
        self.type = None
        self.short = None
        self.color = None
        self.brand = None
        self.main_category_id = None
        self.description_category_id = None
        self.type_id = None
        self.color_id = None
        self.raw_type = None
        self.brand_id = None
        self.parse_data_from_name(x)

    def type_detector(self, x) -> str:
        item_types = {
            "АЗУ": "Автомобильное зарядное устройство",
            "Автомобильный видеорегистратор": "Видеорегистратор",
            "Аккумулятор внешний": "Внешний аккумулятор",
            "Аккумулятор внешний беспроводной": "Внешний аккумулятор",
            "Аккумулятор для экшн-камеры": "Аксессуар для экшн-камеры",
            "Аккумулятор сменный": "Запчасть для робота-пылесоса",
            "Аккумулятор сменный д/Mi": "Запчасть для робота-пылесоса",
            "Аэрогриль": "Аэрогриль",
            "Бумага для фотопринтера": "Фотобумага",
            "Бутылка спортивная": "Бутылка",
            "Весы": "Напольные весы",
            "Видеокамера": "Камера видеонаблюдения",
            "Видеокамера безопасности": "Камера видеонаблюдения",
            "Графический планшет": "Графический планшет",
            "Дальномер лазерный": "Дальномер",
            "Датчик движения и освещения": "Датчик движения",
            "Датчик освещенности": "Датчик движения",
            "Датчик открытия": "Датчик движения",
            "Датчик температуры и влажности": "Датчик движения",
            "Дозатор жидкого мыла автоматический": "Дозатор винтовой для жидкого мыла",
            "Дозатор сенсорный": "Дозатор винтовой для жидкого мыла",
            "Док-станция для зарядки": "Док-станция",
            "Дрель-шуруповерт": "Дрель-шуруповерт",
            "Звонок дверной умный": "Автоматика для дверей",
            "Зеркало": "Зеркало косметическое",
            "Зонт": "Зонт",
            "Зонт автоматический": "Зонт",
            "Зубная щетка": "Электрическая зубная щетка",
            "Зубная щетка ирригатор": "Электрическая зубная щетка",
            "Зубная щётка": "Электрическая зубная щетка",
            "Измеритель качества воды": "Тестер качества воды",
            "Ирригатор портативный": "Ирригатор",
            "Кабель": "Кабель питания",
            "Кабель д/зарядки": "Кабель питания",
            "Кабель-переходник": "Кабель питания",
            "Карта памяти": "Карта памяти",
            "Картридж для кормушки автоматической": "Миска для животных",
            "Квадрокоптер": "Квадрокоптер",
            "Клипса для бега": "Набор для фитнеса",
            "Колонка портативная": "Беспроводная акустика",
            "Колонка умная": "Умная колонка",
            "Комплект": "Аксессуар для робота-пылесоса",
            "Комплект аксессуаров": "Аксессуар для робота-пылесоса",
            "Комплект боковых щёток": "Аксессуар для робота-пылесоса",
            "Комплект держатель салфетки": "Аксессуар для робота-пылесоса",
            "Комплект салфеток": "Аксессуар для робота-пылесоса",
            "Комплект салфеток для влажной уборки": "Аксессуар для робота-пылесоса",
            "Комплект салфеток для робота-пылесоса": "Аксессуар для робота-пылесоса",
            "Комплект фильтр+щётка": "Аксессуар для робота-пылесоса",
            "Комплект фильтров": "Аксессуар для робота-пылесоса",
            "Комплект фильтров и щеток-роликов": "Аксессуар для робота-пылесоса",
            "Комплект фильтров и щёток": "Аксессуар для робота-пылесоса",
            "Комплект насадок для ирригатора": "Насадка для ирригатора",
            "Компрессор": "Компрессор автомобильный",
            "Компрессор автомобильный": "Компрессор автомобильный",
            "Кормушка автоматическая": "Автоматическая кормушка",
            "Косметологический аппарат для лечения акне": "Косметологический аппарат",
            "Кофейный набор для приготовления кофе": "Набор кофейный",
            "Кофемашина": "Автоматическая кофемашина",
            "Крепление": "Кронштейн",
            "Кулон": "Украшение для смарт-часов",
            "Кусачки для ногтей": "Средство для ногтей и кутикулы",
            'Лампа': "Умная лампочка",
            'Лампа настольная умная': "Лампа настольная",
            'Лампа прикроватная умная': "Умная лампочка",
            'Лампа умная': "Умная лампочка",
            'Лента светодиодная': "Светодиодная лента",
            'Маршрутизатор': "Роутер",
            'Массажер': "Массажер спортивный",
            'Машинка для стрижки': "Машинка для стрижки",
            'Машинка для удаления катышков': "Машинка для удаления катышков",
            'Мешок-пылесборник': "Аксессуар для пылесоса",
            'Мешок-пылесборник угольный': "Аксессуар для пылесоса",
            'Монитор': "Монитор",
            'Мультиинструмент велосипедный': "Мультитул",
            'Мультитул': "Мультитул",
            'Мышь': "Мышь",
            'Мышь беспроводная': "Мышь",
            'Набор кухонных ножей': "Набор ножей",
            'Набор ножей с подставкой': "Набор ножей",
            'Набор электрических мельниц с аккумулятором': "Электромельница для специй",
            'Насадка': "Насадка для электрической зубной щетки",
            'Насадка д/электрической зубной щетки': "Насадка для электрической зубной щетки",
            'Насадка сменная д/триммера': "Сменные кассеты для мужских бритв",
            'Насадка сменная д/электробритвы': "Сменные кассеты для мужских бритв",
            'Наушники': "Наушники",
            'Наушники беспроводные': "Наушники",
            'Наушники накладные беспроводные': "Наушники",
            'Обогреватель вертикальный': "Обогреватель",
            'Отвертка': "Отвертка",
            'Отвертка аккумуляторная': "Отвертка аккумуляторная",
            'Отвертка электрическая': "Отвертка аккумуляторная",
            'Охлаждающие кубики для напитков': "Охлаждающий стержень для бутылки",
            'Очиститель воздуха': "Очиститель воздуха",
            'Очки солнцезащитные': "Очки солнцезащитные",
            'Переходник сетевой': "Коннектор",
            'Перчатки': "Термоперчатки",
            'Печь микроволновая': "Микроволновая печь",
            'Планшет': "Планшет",
            'Планшет графический': "Графический планшет",
            'Пленка': "Защитная пленка",
            'Пленка гидрогелевая': "Защитная пленка",
            'Пленка гидрогелевая для планшетов': "Защитная пленка",
            'Поилка автоматическая': "Автопоилка",
            'Помпа беспроводная': "Диспенсер для воды",
            'Помпа беспроводная с датчиком качества воды': "Диспенсер для воды",
            'Прибор для чистки и массажа лица': "Массажный прибор",
            'Пульт ДУ': "Пульт ДУ",
            'Пылесос аккумуляторный': "Ручной пылесос",
            'Пылесос вертикальный': "Вертикальный пылесос",
            'Пылесос от пылевых клещей': "Ручной пылесос",
            'Пылесос ручной': "Ручной пылесос",
            'Ремешок': "Ремешок для часов",
            'Ремешок из нержавеющей стали для часов': "Ремешок для часов",
            'Ремешок кожаный для': "Ремешок для часов",
            'Ремешок кожаный для часов': "Ремешок для часов",
            'Ремешок металлический': "Ремешок для часов",
            'Ремешок нейлоновый для': "Ремешок для часов",
            'Ремешок нейлоновый для часов': "Ремешок для часов",
            'Ремешок нейлоновый петлевой для часов': "Ремешок для часов",
            'Ремешок нейлоновый плетёный для часов': "Ремешок для часов",
            'Ремешок силиконовый для': "Ремешок для часов",
            'Ремешок силиконовый для часов': "Ремешок для часов",
            'Ремешок спортивный для часов': "Ремешок для часов",
            'Робот-пылесос': "Робот-пылесос",
            'Ручной отпариватель': "Отпариватель",
            'Рюкзак': "Рюкзак",
            'Рюкзак с LED-дисплеем': "Рюкзак",
            'СЗУ': "Сетевое зарядное устройство",
            'Салфетка губка сменная д/влажной уборки д/пылесоса': "Аксессуар для пылесоса",
            'Салфетка губка сменная д/влажной уборки одноразовая д/пылесоса': "Аксессуар для пылесоса",
            'Салфетка сменная д/влажной уборки д/пылесоса': "Аксессуар для пылесоса",
            'Саундбар': "Саундбар",
            'Светильник портативный': "Светильник-переноска",
            'Светильник потолочный': "Умный светильник",
            'Сетевое зарядное устройство': "Сетевое зарядное устройство",
            'Смарт-часы': "Умные часы",
            'Смартфон': "Смартфон",
            'Средство для моющих пылесосов': "Аксессуар для пылесоса",
            'Средство для чистки экранов': "Универсальное чистящее средство",
            'Стекло защитное': "Защитное стекло",
            'Стилус-указатель': "Стилус",
            'Сумка': "Велосумка",
            'Сумка-шоппер': "Сумка с ручками",
            'Сушилка для обуви': "Сушилка для обуви",
            'ТВ-приставка': "ТВ-тюнер",
            'Таблетки от накипи для чайников и кофеварок': "Картридж от накипи",
            'Телевизор': "Телевизор",
            'Термокружка': "Термокружка",
            'Точилка для ножей': "Точилка для ножей, ножниц",
            'Триммер': "Триммер для бороды и усов",
            'Триммер для носа': "Триммер для носа и ушей",
            'Тряпка для швабры': "Тряпка",
            'Увлажнитель воздуха': "Увлажнитель воздуха",
            'Удлинитель ленты светодиодной': "Коннектор для светодиодной ленты",
            'Умная колонка Яндекс Станция Миди с Алисой с': "Умная колонка",
            'Умная колонка ЯндексСтанция Дуо Макс с Алисой с': "Умная колонка",
            'Умная колонка ЯндексСтанция Лайт бежевый': "Умная колонка",
            'Умная колонка ЯндексСтанция Лайт жёлтый': "Умная колонка",
            'Умная колонка ЯндексСтанция Лайт зеленый': "Умная колонка",
            'Умная колонка ЯндексСтанция Лайт красный': "Умная колонка",
            'Умная колонка ЯндексСтанция Лайт розовый': "Умная колонка",
            'Умная колонка ЯндексСтанция Макс с Алисой с': "Умная колонка",
            'Умная колонка ЯндексСтанция Мини Плюс с часами красный': "Умная колонка",
            'Умная колонка ЯндексСтанция Мини Плюс с часами серый': "Умная колонка",
            'Умная колонка ЯндексСтанция Мини Плюс с часами синий': "Умная колонка",
            'Умная колонка ЯндексСтанция Мини Плюс с часами черный': "Умная колонка",
            'Умная колонка ЯндексСтанция бежевый': "Умная колонка",
            'Умная колонка ЯндексСтанция синий': "Умная колонка",
            'Умная колонка': 'Умная колонка',
            'Умная розетка': "Умная розетка",
            'Умные часы': "Умные часы",
            'Усилитель сигнала': "Усилитель сигнала",
            'Устройство зарядное автомобильное': "Автомобильное зарядное устройство",
            'Устройство зарядное беспроводное': "Беспроводное зарядное устройство",
            'Устройство зарядное сетевое': "Сетевое зарядное устройство",
            'Фен': "Фен для волос",
            'Фен для волос': "Фен для волос",
            'Фильтр': "Аксессуар для пылесоса",
            'Фильтр д/очистителя воздуха': "Аксессуар для очистителя воздуха",
            'Фильтр для поилки автоматической': "Фильтр для поилки",
            'Фильтр сменный д/пылесоса': "Аксессуар для пылесоса",
            'Фильтр-мешок': "Аксессуар для пылесоса",
            'Фитнес браслет': "Фитнес-браслет",
            'Фитнес трекер': "Фитнес-браслет",
            'Флеш-накопитель': "USB-флеш-накопитель",
            'Фонарь многофункциональный': "Карманный фонарь",
            'Центр управления умным домом': "Модуль управления",
            'Чайник электрический': "Электрический чайник",
            'Часы-термогигрометр': "Термогигрометр",
            'Чемодан': "Чемодан",
            'Чехол': "Чехол для смартфона",
            'Чехол для': "Чехол для смартфона",
            'Чехол-книжка': "Чехол для смартфона",
            'Чехол-книжка для планшета': "Чехол для смартфона",
            'Чистящее средство-спрей': "Универсальное чистящее средство",
            'Швабра': "Швабра",
            'Штопор': "Электрический штопор",
            'Штопор с винным набором': "Электрический штопор",
            'Штопор электрический': "Электрический штопор",
            'Щетка боковая д/пылесоса': "Аксессуар для робота-пылесоса",
            'Щетка зубная': "Электрическая зубная щетка",
            'Щетка зубная электрическая ультразвуковая': "Электрическая зубная щетка",
            'Щетка основная д/пылесоса': "Аксессуар для робота-пылесоса",
            'Щетка роликовая': "Аксессуар для робота-пылесоса",
            'Щётка боковая': "Аксессуар для робота-пылесоса",
            'Щётка боковая для робота-пылесоса': "Аксессуар для робота-пылесоса",
            'Щётка основная': "Аксессуар для робота-пылесоса",
            'Щётка основная разборная': "Аксессуар для робота-пылесоса",
            'Щётки-ролики': "Аксессуар для робота-пылесоса",
            'Электрическая мельница': "Электромельница для специй",
            'Электрическая мельница со встроенным аккумулятором': "Электромельница для специй",
            'Электрическая мясорубка': "Мясорубка",
            'Электрический стабилизатор для экшн-камеры': "Стабилизатор для камеры",
            'Электробритва': "Электробритва",
            'Электросамокат': "Электросамокат",
            'L-образная площадка': 'Держатель для фотооборудования',
            'Аккумулятор серии': 'Зарядное устройство для фото-видеотехники',
            'Аксессуары': 'Аксессуар для игровой приставки',
            'Акустическая система': 'Акустическая система',
            'Беззеркальный фотоаппарат': 'Беззеркальный фотоаппарат',
            'Беспроводная гарнитура': 'Аксессуар для игровой приставки',
            'Беспроводная игровая гарнитура': 'Аксессуар для игровой приставки',
            'Беспроводная колонка для вечеринок': 'Акустическая система',
            'Беспроводной контроллер': 'Геймпад',
            'Бленда': 'Бленда',
            'Брелок': 'Брелок',
            'Вертикальная рукоятка': 'Держатель для фото',
            'Виниловый проигрыватель': 'Виниловый проигрыватель',
            'Внешний аккумулятор': 'Внешний аккумулятор',
            'Геймпад': 'Геймпад',
            'Дата-кабель': 'Кабель питания',
            'Держатель смартфона автомобильный': 'Держатель автомобильный',
            'Джойстик-руль': 'Руль игровой',
            'Домашний кинотеатр': 'Домашний кинотеатр',
            'Зарядная станция': 'Подставка для геймпада',
            'Защитная накладка': 'Аксессуар для игровой приставки',
            'Защитная полужесткая пленка': 'Кейс для камеры',
            'Защитное стекло': 'Чехол + защитное стекло/пленка для смартфона',
            'Защитные накладки': 'Аксессуар для игровой приставки',
            'Защитные накладки силиконовые': 'Аксессуар для игровой приставки',
            'Защитный чехол для кабеля': 'Чехол для инструментов',
            'Игра': 'Видеоигра',
            'Игра Ведьмак Дикая Охота. Издание «Игра года»': 'Видеоигра',
            'Игра Дожить до рассвета. (Хиты': 'Видеоигра',
            'Игра Одни из нас. Обновленная версия': 'Видеоигра',
            'Игра Одни из нас. Обновленная версия (Хиты': 'Видеоигра',
            'Игра Орден': 'Видеоигра',
            'Игра Призрак Цусимы. Режиссерская версия': 'Видеоигра',
            'Игровая приставка': 'Игровая консоль',
            'Кабель питания': 'Кабель питания',
            'Кабель питания-данных': 'Кабель питания',
            'Карта памяти серии': 'Карта памяти',
            'Колонка': 'Беспроводная колонка',
            'Коммутационный кабель': 'Кабель питания',
            'Консоль': 'Игровая консоль',
            'Крепеж': 'Аксессуар для экшн-камеры',
            'Крепление на руку': 'Аксессуар для экшн-камеры',
            'Музыкальный центр': 'Музыкальный центр',
            'Набор универсальных креплений': 'Аксессуар для экшн-камеры',
            'Накладка': 'Чехол для смартфона',
            'Накладка силиконовая': 'Чехол для смартфона',
            'Накладка усиленная': 'Чехол для смартфона',
            'Переходник': 'Кабель-переходник',
            'Пластиковая накладка': 'Чехол для смартфона',
            'Пластиковая накладка усиленная': 'Чехол для смартфона',
            'Пневматический очиститель': 'Специальное чистящее средство',
            'Подставка светодиодная для': 'Аксессуар для игровой приставки',
            'Постер': 'Постер',
            'Пульт голосовой': 'Пульт ДУ',
            'Пылесос беспроводной': 'Ручной пылесос',
            'Светильник': 'Аксессуар для игровой приставки',
            'Силиконовая накладка': 'Аксессуар для игровой приставки',
            'Средство для очистки экранов телевизоров и мониторов с салфеткой': 'Специальное чистящее средство',
            'Стабилизатор': 'Аксессуар для экшн-камеры',
            'Стайлер': 'Стайлер',
            'Стекло': 'Защитное стекло',
            'Стенд многофункциональный': 'Охлаждение для консоли',
            'ТВ-адаптер': 'ТВ-тюнер',
            'ТВ-медиацентр': 'ТВ-тюнер',
            'Твердотельный накопитель': 'Внешний SSD-диск',
            'Телевизор Яндекс ТВ станция с Алисой': 'Телевизор',
            'Умная колонка Яндекс Станция Миди с Алисой, с': 'Умная колонка',
            'Умная колонка Яндекс.Станция Дуо Макс с Алисой, с': 'Умная колонка',
            'Умная колонка Яндекс.Станция Лайт, бежевая': 'Умная колонка',
            'Умная колонка Яндекс.Станция Лайт, жёлтая': 'Умная колонка',
            'Умная колонка Яндекс.Станция Лайт, зеленая': 'Умная колонка',
            'Умная колонка Яндекс.Станция Лайт, розовая': 'Умная колонка',
            'Умная колонка Яндекс.Станция Лайт, фиолетовая': 'Умная колонка',
            'Умная колонка Яндекс.Станция Макс с Алисой, с': 'Умная колонка',
            'Умная колонка Яндекс.Станция Мини плюс с часами, красная': 'Умная колонка',
            'Умная колонка Яндекс.Станция Мини плюс с часами, серая': 'Умная колонка',
            'Умная колонка Яндекс.Станция Мини плюс с часами, черная': 'Умная колонка',
            'Умный светильник': 'Умный светильник',
            'Цветная светодиодная подсветка': 'Светодиодная панель',
            'Чехол-подставка для': 'Чехол для смартфона',
            'Чехол-футляр': 'Сумка для фото-видеотехники',
            'Чистящее средство': 'Универсальное чистящее средство',
            'Шлем виртуальной реальности': 'VR-очки',
            'Шнур сетевой': 'Сетевой шнур с вилкой',
            'Шнур сетевой для ТВ,': 'Сетевой шнур с вилкой'
        }
        x = x.split()
        item_type = []
        for part in x:
            try:
                if detect(part) in ['ru', 'uk', 'bg', 'mk']:
                    item_type.append(part)
                else:
                    break
            except Exception:
                continue
        self.raw_type = " ".join(item_type)
        r = item_types.get(" ".join(item_type))
        return r

    @staticmethod
    def cleaner(x):
        clean = [";", ":", ",", ".", "!", "?", "'", '"', "(", ")", "{", "}",
                 "[", "]", "<", ">", "&", "|", "^", "%", "$", "#"]
        for symbol in clean:
            x = x.replace(symbol, '')
        return x.lstrip().rstrip()

    def color_detector(self, x) -> str:
        for subs in ('ая', 'ое', 'ые',):
            x = x.replace(subs, 'ый')
        x = x.replace('ё', 'е')
        colors_english = [
            "red",
            "blue",
            "green",
            "yellow",
            "orange",
            "purple",
            "pink",
            "brown",
            "black",
            "white",
            "gray",
            "turquoise",
            "gold",
            "silver",
            "lavender",
            "raspberry",
            "peach",
            "mint",
            "salad green",
            "beige",
            "emerald",
            "sky blue",
            "fuchsia",
            "coral",
            "plum",
            "terracotta",
            "khaki",
            "ochre",
            "cornflower blue",
            "ivory",
            "seafoam",
            "dusty pink",
            "scarlet",
            "burgundy",
            "light green",
            "navy blue",
            "light blue",
            "caramel",
            "dark green",
            "salmon",
            "bay",
            "slate blue",
            "light yellow",
            "dark brown",
            "mint green",
            "pistachio",
            "light gray",
            "amber",
            "lavender blue",
            "teal"
        ]
        color_vals = {
            'абрикосовый': 972075715,
            'абрикосовый крайола': 972075911,
            'авокадо': 972075796,
            'агатовый серый': 972075830,
            'айвори': 972075625,
            'аквамариновый': 972075698,
            'акулья кожа': 972075970,
            'алоэ': 972075976,
            'алый': 972075614,
            'амарантово-розовый': 972075917,
            'амарантовый': 972076015,
            'аметистовый': 972075809,
            'античная бронза': 972076079,
            'античное золото': 972076080,
            'античный белый': 972075729,
            'античный розовый': 972075811,
            'антрацитово-серый': 972075725,
            'антрацитовый': 972075570,
            'апельсин': 972076085,
            'атласное серебро': 972075756,
            'бабл гам': 972076069,
            'баклажановый': 972075637,
            'банановый': 972075876,
            'бежево-розовый': 972075748,
            'бежевый': 61573,
            'бежевый глянец': 972075846,
            'бежевый лайт': 972075521,
            'бежевый меланж': 972075537,
            'бежевый нейтральный': 972075676,
            'бежевый прозрачный': 972075875,
            'бело-зеленый': 972075684,
            'бело-розовый': 972075768,
            'бело-серый': 972075574,
            'бело-синий': 972075628,
            'бело-терракотовый': 972075891,
            'белый': 61571,
            'белый бриллиант': 972075629,
            'белый глянец': 972075598,
            'белый иней': 972075575,
            'белый матовый': 972075543,
            'белый мрамор': 972075566,
            'белый муар': 972075978,
            'белый песок': 972075631,
            'белый текстурный': 972075666,
            'белый шоколад': 972075668,
            'бирюзово-зеленый': 972075640,
            'бирюзовый': 61595,
            'бирюзовый иней': 972075950,
            'бледно-бирюзовый': 972075983,
            'бледно-бордовый': 972076020,
            'бледно-голубой': 972075652,
            'бледно-желтый': 972075558,
            'бледно-зеленый': 972075861,
            'бледно-коричневый': 972075732,
            'бледно-лиловый': 972075795,
            'бледно-пурпурный': 972075985,
            'бледно-розовый': 972075559,
            'бледно-синий': 972075986,
            'блестящий пурпурный': 972075928,
            'болотный': 972075615,
            'бордово-фиолетовый': 972075726,
            'бордовый': 61590,
            'бордовый меланж': 972075769,
            'брезентово-серый': 972076058,
            'бриллиантово-синий': 972075721,
            'бронза': 61587,
            'бронзово-оливковый': 972076028,
            'бронзовый': 972075523,
            'брусничный': 972075747,
            'бургунди': 972075899,
            'бутылочный': 972075945,
            'бэби-голубой': 972075753,
            'бэби-розовый': 972075696,
            'ванильно-бежевый': 972075548,
            'ванильный': 972075688,
            'васаби': 972076040,
            'васильковый': 972075549,
            'венге': 972075632,
            'верблюжий': 972075946,
            'вереск': 972076062,
            'вери пери': 972075918,
            'винно-красный': 972075870,
            'винный': 972075607,
            'вишнево-красный': 972075649,
            'вишневый': 972075622,
            'вишня': 972075967,
            'галопогосский зеленый': 972076047,
            'глубокий зеленый': 972075788,
            'глубокий коралловый': 972075975,
            'глубокий коричневый': 972075584,
            'глубокий красный': 972075613,
            'глубокий пурпурно-розовый': 972075969,
            'глубокий пурпурный': 972075960,
            'глубокий розовый': 972075857,
            'глубокий сине-зеленый': 972075759,
            'глубокий фиолетовый': 972075738,
            'глубокий черный': 972075512,
            'голландский синий': 972075932,
            'голубая ель': 972075944,
            'голубика': 972075897,
            'голубино-синий': 972075594,
            'голубой': 61584,
            'голубой берилл': 972075784,
            'голубой лед': 972075606,
            'голубой меланж': 972075601,
            'голубой тиффани': 972075627,
            'голубой туман': 972075731,
            'голубые джинсы': 972075673,
            'горчичный': 258411664,
            'горчичный меланж': 972075905,
            'горький шоколад': 972075817,
            'гранатовый': 972075819,
            'графит': 972075518,
            'грязно-голубой': 972076043,
            'деним': 972076077,
            'джинс': 972075546,
            'джинсовый меланж': 972075714,
            'дымка': 972076089,
            'дымчатая роза': 972075860,
            'дымчатый': 972075981,
            'дымчатый синий': 972075994,
            'ежевичный': 972075999,
            'еловый лес': 972076027,
            'желто-зеленый': 972075682,
            'желто-зеленый светлый': 972075813,
            'желто-коричневый': 972075912,
            'желто-красный': 972075832,
            'желто-оранжевый': 972075687,
            'желто-розовый': 972075896,
            'желтый': 61578,
            'желтый бархат': 972075835,
            'желтый крайола': 972075866,
            'желтый матовый': 972075929,
            'желтый меланж': 972075920,
            'желтый неон': 972075705,
            'желтый тюльпан': 972075842,
            'жемчужно-белый': 972075624,
            'жемчужно-голубой': 972075968,
            'жемчужно-розовый': 972075993,
            'жемчужный': 972075579,
            'жемчужный серый': 972075647,
            'жимолость': 972076095,
            'защитный хаки': 972075699,
            'зеленая груша': 972076090,
            'зеленая мята': 972076078,
            'зеленая оливка': 972076075,
            'зеленка': 972075886,
            'зелено-серый': 972075826,
            'зеленовато-бежевый': 972075780,
            'зеленовато-серый': 972075790,
            'зеленовато-синий': 972075765,
            'зеленое море': 972075704,
            'зеленое стекло': 972075908,
            'зеленый': 61583,
            'зеленый бархат': 972075609,
            'зеленый дым': 972075746,
            'зеленый лист': 972075658,
            'зеленый лишайник': 972075924,
            'зеленый меланж': 972075766,
            'зеленый мох': 972075723,
            'зеленый неон': 972075646,
            'зелёный блеск': 972075868,
            'зеркальный': 970693003,
            'зернистый бордовый': 972076029,
            'зернистый светло-бежевый': 972076025,
            'зернистый светло-серый': 972076048,
            'зернистый серо-голубой': 972076070,
            'зернистый серый': 972076031,
            'зернистый темно-зеленый': 972076063,
            'зернистый темно-серый': 972076039,
            'зернистый темно-синий': 972076064,
            'зернистый черный': 972075879,
            'золотисто-бежевый': 972075667,
            'золотисто-коричневый': 972075799,
            'золотистый': 972075510,
            'золотой': 61582,
            'изумрудно-зеленый': 972075529,
            'изумрудный': 972075527,
            'изумрудный меланж': 972075837,
            'индиго': 972075555,
            'инжирный': 972076054,
            'ирисовый': 972076002,
            'иссиня-черный': 972075588,
            'какао': 972075586,
            'камень': 972075947,
            'камуфляж': 972076073,
            'канареечный': 972076065,
            'капучино': 972075531,
            'карамельный': 972075651,
            'карбон': 972075966,
            'кармин': 972076049,
            'каштановый': 972076094,
            'кирпично-красный': 972075709,
            'кирпичный': 972075816,
            'кобальт': 972075872,
            'кокосовое молоко': 972076100,
            'конфетно-розовый': 972076013,
            'коньячный': 972075831,
            'кораллово-красный': 972075592,
            'коралловый': 61601,
            'коралловый темный': 972075964,
            'корица': 972075786,
            'коричневато-розовый': 972075801,
            'коричневая горчица': 972075719,
            'коричнево-горчичный мелан': 972075887,
            'коричнево-красный': 61603,
            'коричнево-серый': 972075650,
            'коричневый': 61575,
            'коричневый крайола': 972075855,
            'коричневый меланж': 972075697,
            'коричневый мрамор': 972075711,
            'коричневый перламутровый': 972075901,
            'коричневый ротанг': 972075841,
            'королевский розовый': 972075802,
            'королевский синий': 972075654,
            'кофе': 972075644,
            'кофе с молоком': 972075610,
            'кофейная роза': 972075941,
            'кофейный': 972075530,
            'кофейный десерт': 972076019,
            'краплак красный': 972076032,
            'красная слива': 972076067,
            'красно-коричневый': 972075587,
            'красно-оранжевый': 972075717,
            'красно-пурпурный': 972075845,
            'красно-розовый меланж': 972075847,
            'красно-сиреневый': 972075764,
            'красновато-бордовый': 972075581,
            'красный': 61579,
            'красный бархат': 972075620,
            'красный виноград': 972075894,
            'красный каркаде': 972075778,
            'красный матовый': 972075806,
            'красный песок': 972075869,
            'крафт': 972075662,
            'крем-брюле': 972075771,
            'кремово-белый': 972075639,
            'кремовый': 258411648,
            'кремовый капучино': 972075700,
            'кукурузный': 972075922,
            'кэмел': 972075733,
            'лавандово-розовый': 972075824,
            'лавандово-серый': 972076016,
            'лавандовый': 972075535,
            'лазурно-серый': 972075706,
            'лазурный': 258411643,
            'лайм': 972075660,
            'латте': 972075777,
            'латунь': 972076082,
            'лен': 972076011,
            'леопардовый': 972075572,
            'лиловый': 971039569,
            'лимонно-желтый': 972075727,
            'лимонно-зеленый': 972076023,
            'лимонный': 972075599,
            'лимонный крем': 972075974,
            'лососевый': 972075838,
            'льняной': 972076084,
            'маджента': 972076061,
            'маджента розовый': 972075961,
            'малахит': 972075791,
            'малиново-красный': 972075737,
            'малиново-розовый': 972075552,
            'малиновый': 970671252,
            'мандариновый': 972075952,
            'маренго': 972075942,
            'марсала': 972075762,
            'матовое золото': 972076074,
            'махагон': 972076024,
            'медно-коричневый': 972075995,
            'медно-розовый': 972076036,
            'медный': 972075653,
            'медово-бежевый': 972075893,
            'медовый': 972076088,
            'медь': 61609,
            'ментол': 972075577,
            'металл': 972075556,
            'милитари': 972076087,
            'мокко': 972075621,
            'мокрый асфальт': 972075718,
            'молочная корица': 972076000,
            'молочно-голубой': 972076026,
            'молочный': 972075511,
            'молочный шоколад': 972075661,
            'морковный': 972075840,
            'морская волна': 972075569,
            'морская глубина': 972076059,
            'морской': 972075750,
            'морской зеленый': 972075810,
            'мох': 972076086,
            'мохито': 972076051,
            'мрамор': 972075692,
            'мышино-серый': 972075757,
            'мягкий белый': 972075547,
            'мягкий розовый': 972075538,
            'мята пыльная': 972075852,
            'мятно-бирюзовый': 972075595,
            'мятно-серый': 972075938,
            'мятный': 972075515,
            'насыщенный бежевый': 972075844,
            'насыщенный желтый': 972075877,
            'насыщенный коричневый': 972075739,
            'натуральный зеленый': 972075926,
            'натуральный кремовый': 972076096,
            'натуральный серый': 972075873,
            'небесно-голубой': 972075519,
            'небесный': 972075681,
            'нежная мята': 972075779,
            'нежно-голубой': 972075616,
            'нежный коралл': 972075850,
            'нежный розовый': 972075563,
            'незрелый желтый': 972075940,
            'ниагара': 972076044,
            'ночной синий': 972075963,
            'нюдовый': 972075643,
            'облепиха': 972076034,
            'огненно-красный': 972075734,
            'океан': 972075925,
            'оливково-зеленый': 972075787,
            'оливково-серый': 972075951,
            'оливковый': 61605,
            'оникс': 972076037,
            'оранжево-желтый': 972075580,
            'оранжево-красный': 972075659,
            'оранжево-розовый': 972075751,
            'оранжевый': 61585,
            'оранжевый витамин': 972075798,
            'оранжевый неон': 972075752,
            'охотничий зеленый': 972075707,
            'охра': 972075760,
            'охра желтая': 972075943,
            'палисандр': 972076101,
            'пастельно-бирюзовый': 972076038,
            'пастельно-голубой': 972075730,
            'пастельно-коричневый': 972075888,
            'пастельно-мятный': 972075863,
            'пастельно-оранжевый': 972075858,
            'пастельно-песочный': 972075931,
            'пастельно-розовый': 972075520,
            'пастельно-салатовый': 972075936,
            'пастельно-серый': 972075763,
            'пастельно-синий': 972076006,
            'пастельно-сиреневый': 972075827,
            'пастельно-фиолетовый': 972075815,
            'пастельный темно-синий': 972075959,
            'пепел': 972075833,
            'пепельно-коричневый': 972075708,
            'перламутрово-зелёный': 972075859,
            'перламутрово-оранжевый': 972075910,
            'перламутрово-розовый': 972075839,
            'перламутрово-рубиновый': 972076060,
            'перламутровый': 971039568,
            'перламутровый голубой': 972075930,
            'персидский индиго': 972076057,
            'персидский красный': 972076050,
            'персиковая нуга': 972076004,
            'персиково-розовый': 972075701,
            'персиковый': 972075522,
            'персиковый крайола': 972075703,
            'персиковый крем': 972076092,
            'персиковый мусс': 972076102,
            'песочно-желтый': 972075742,
            'песочный': 972075524,
            'петрол': 972075902,
            'пигментный зеленый': 972076055,
            'пломбир': 972076033,
            'полынь': 972075808,
            'приглушенно-белый': 972075972,
            'прозрачный': 61572,
            'прозрачный кристалл': 972075554,
            'пудровый': 972075514,
            'пурпур': 972075792,
            'пурпурно-красный': 972075728,
            'пурпурно-розовый': 972075851,
            'пурпурно-синий': 972075904,
            'пурпурный': 970628491,
            'пшеничный': 972075892,
            'пыльная роза': 972075553,
            'пыльная сирень': 972075767,
            'пыльно-оливковый': 972075889,
            'пыльный бежевый': 972075655,
            'пыльный голубой': 972076007,
            'радикальный красный': 972076012,
            'разноцветный': 369939085,
            'резедово-зеленый': 972076021,
            'рождественский зеленый': 972075984,
            'розовато-серый': 972075702,
            'розовая гвоздика': 972075829,
            'розовая долина': 972075880,
            'розовая платина': 972076076,
            'розовая пудра': 972075541,
            'розовая фуксия': 972075557,
            'розово-золотой': 972075638,
            'розово-коралловый': 972075761,
            'розово-коричневый': 972075710,
            'розово-лавандовый': 972075789,
            'розово-пурпурный': 972075754,
            'розово-фиолетовый': 972075803,
            'розовое золото': 972075634,
            'розовое облако': 972075740,
            'розовый': 61580,
            'розовый антик': 972075890,
            'розовый гранат': 972076009,
            'розовый грейфрут': 972075909,
            'розовый дым': 972075693,
            'розовый жемчуг': 972075695,
            'розовый кварц': 972075818,
            'розовый лимонад': 972075785,
            'розовый меланж': 972075716,
            'розовый нектар': 972075939,
            'розовый неон': 972075670,
            'розовый нюд прозрачный': 972075916,
            'розовый персик': 972075724,
            'розовый песок': 972075823,
            'розовый тауп': 972075853,
            'розовый фарфор': 972075962,
            'розовый фламинго': 972075630,
            'роскошное какао': 972075998,
            'рубиновый': 972075836,
            'рыжевато-коричневый': 972075807,
            'рыжий': 972075545,
            'рыжий терракот': 972075773,
            'салатовый': 258411659,
            'сапфирово-синий': 972075685,
            'сапфировый': 972075800,
            'сатиновое золото': 972076083,
            'свежий мятный': 972075953,
            'светлая фиалка': 972075990,
            'светло серо-зеленый': 972075848,
            'светло-бежевый': 61593,
            'светло-бирюзовый': 972075582,
            'светло-голубой': 972075528,
            'светло-желтый': 970673967,
            'светло-зеленый': 61589,
            'светло-золотистый': 972075617,
            'светло-каштановый': 972076103,
            'светло-коралловый': 972075849,
            'светло-коричневый': 61591,
            'светло-оливковый': 972075772,
            'светло-оранжевый': 972075722,
            'светло-персиковый': 972075895,
            'светло-песочный': 972075636,
            'светло-петрольный': 972076053,
            'светло-пурпурный': 972075980,
            'светло-розовый': 61596,
            'светло-салатовый': 972075935,
            'светло-серый': 61594,
            'светло-серый меланж': 972075619,
            'светло-синий': 971001201,
            'светло-сиреневый': 972075605,
            'светло-фиолетовый': 972075562,
            'светлое дерево': 972075657,
            'светлое какао': 972075871,
            'светлый антрацит': 972076008,
            'светлый графит': 972076001,
            'светлый джинс': 972075774,
            'светлый опаловый': 972076045,
            'светлый песок': 972075903,
            'светлый синевато-зеленый': 972076022,
            'светлый фисташковый': 972075794,
            'светлый хаки': 972075648,
            'сгоревший желтый': 972075992,
            'сердолик': 972076030,
            'серебристо-белый': 972075576,
            'серебристо-голубой': 972076005,
            'серебристо-зеленый': 972076056,
            'серебристо-коричневый': 972076052,
            'серебристо-красный': 972076066,
            'серебристо-серый': 972075672,
            'серебристый': 61610,
            'серебристый меланж': 972075854,
            'серебристый пион': 972075979,
            'серебристый туман': 972075900,
            'серебро': 972075513,
            'серо-бежевый': 972075533,
            'серо-бежевый светлый': 972075656,
            'серо-голубой': 972075532,
            'серо-голубой светлый': 972075690,
            'серо-зеленый': 972075564,
            'серо-зеленый джинсовый': 972075949,
            'серо-коричневый': 972075565,
            'серо-синий': 972075539,
            'серо-фиолетовый': 972075677,
            'серо-черный': 972075691,
            'серовато-зеленый': 972075679,
            'серовато-красный': 972075971,
            'серовато-пурпурный': 972075948,
            'серовато-розовый': 972075776,
            'серый': 61576,
            'серый гранит': 972075603,
            'серый графит': 972075540,
            'серый деним': 972075812,
            'серый лист': 972075933,
            'серый меланж': 972075517,
            'серый металлик': 61577,
            'серый шелк': 972075720,
            'сигнальный серый': 972075885,
            'сигнальный синий': 972075906,
            'сине-бирюзовый': 972075881,
            'сине-морской': 972075597,
            'сине-серый': 972075680,
            'сине-фиолетовый': 972075664,
            'синевато-зеленый': 972075781,
            'синевато-серый': 972075783,
            'синий': 61581,
            'синий бархат': 972075596,
            'синий кобальт': 972075561,
            'синий космос': 972075602,
            'синий лист': 972075907,
            'синий лён': 972075743,
            'синий меланж': 972075675,
            'синий неон': 972075822,
            'синий персидский': 972075914,
            'синий петроль': 972075683,
            'синий серый': 972075770,
            'синий топаз': 972075821,
            'синяя волна': 972075736,
            'синяя лазурь': 972075865,
            'сиреневый': 61588,
            'сиреневый меланж': 972075745,
            'сливовый': 972075635,
            'сливочная помадка': 972076014,
            'сливочный': 972075927,
            'слоновая кость': 61597,
            'солнечно-желтый': 972075573,
            'соломенный': 972075919,
            'сочный гранат': 972075884,
            'средне-серый': 972075593,
            'средне-серый меланж': 972075793,
            'сталь': 972075834,
            'стальной голубой': 972075898,
            'стальной графит': 972076081,
            'сумеречный': 972076046,
            'сумрачно-белый': 972075977,
            'супер белый': 972075551,
            'суровый темно-синий': 972075805,
            'сухая зелень': 972076099,
            'сухая роза': 972075988,
            'табачный': 972075957,
            'тауп': 972075867,
            'телесный': 972075544,
            'темная вишня': 972075883,
            'темная зеленая оливка': 972075797,
            'темная лаванда': 972075913,
            'темная мята': 972076003,
            'темная сирень': 972075864,
            'темная слива': 972075991,
            'темная фуксия': 972075828,
            'темно серо-зеленый': 972075878,
            'темно-алый': 972075923,
            'темно-бежевый': 61604,
            'темно-бирюзовый': 972075645,
            'темно-бордовый': 970832145,
            'темно-бурый': 972075987,
            'темно-голубой': 972075604,
            'темно-горчичный': 972075937,
            'темно-желтый': 972075782,
            'темно-зеленый': 61602,
            'темно-каштановый': 972076091,
            'темно-коричневый': 61598,
            'темно-красный': 972075578,
            'темно-лазурный': 972075934,
            'темно-оливковый': 972075775,
            'темно-оранжевый': 972075713,
            'темно-персиковый': 972075965,
            'темно-пурпурный': 972075958,
            'темно-розовый': 61611,
            'темно-серый': 61600,
            'темно-серый меланж': 972075591,
            'темно-синий': 61592,
            'темно-синий графитовый': 972075689,
            'темно-синий джинсовый': 972075608,
            'темно-фиолетовый': 972075585,
            'темный бронзовый': 972076017,
            'темный горький шоколад': 972075874,
            'темный дуб': 972076098,
            'темный желто-зеленый': 972076018,
            'темный синий меланж': 972075758,
            'темный хаки': 972075618,
            'теплый бежевый': 972075665,
            'теплый белый': 972075526,
            'теплый серый': 972075856,
            'терракот': 972076097,
            'терракот меланж': 972076104,
            'терракотовый': 972075600,
            'терракотовый меланж': 972076035,
            'тиффани': 972075686,
            'томатный': 972076071,
            'топаз': 972076042,
            'топленое молоко': 972075741,
            'травяной зеленый': 972075612,
            'тускло-розовый': 972075862,
            'тускло-сиреневый': 972075814,
            'ультрамариновый': 972075843,
            'умеренно зеленый': 972075825,
            'умеренный красный': 972075989,
            'умеренный розовый': 972075997,
            'фиалковый': 972075755,
            'фиолетово-баклажанный': 972075642,
            'фиолетовый': 61586,
            'фиолетовый меланж': 972075633,
            'фисташковый': 972075550,
            'французский синий': 972076010,
            'фуксия': 61599,
            'фундук': 972076068,
            'хаки': 258411654,
            'холодная полынь': 972076041,
            'холодный белый': 972075542,
            'холодный зеленый': 972075820,
            'холодный фиолетовый': 972075956,
            'хром': 970726613,
            'цветочный розовый': 972075955,
            'чайная роза': 972075915,
            'чернильный': 972075568,
            'черничный': 972075669,
            'черно-зеленый': 972075749,
            'черно-коричневый': 972075804,
            'черно-красный': 972075641,
            'черно-серый': 61607,
            'черно-синий': 972075735,
            'черный': 61574,
            'черный графит': 972075516,
            'черный каменный': 972075560,
            'черный кварц': 972075712,
            'черный кристалл': 972075534,
            'черный лакированный никел': 972075583,
            'черный матовый': 970671251,
            'черный меланж': 972075525,
            'черный муар': 972075678,
            'черный нюд': 972075744,
            'черный сапфир': 972075589,
            'черный сахара': 972075982,
            'шалфей': 972075882,
            'шампань': 972075611,
            'шафрановый': 972075996,
            'шоколадно-коричневый': 972075674,
            'шоколадный': 61606,
            'шоколадный трюфель': 972075973,
            'эвкалипт': 972075954,
            'экрю': 972076072,
            'электрик': 972075623,
            'ягодный': 972076093,
            'янтарный': 972075694,
            'яркий оранжевый': 972075626,
            'ярко-голубой': 972075671,
            'ярко-желтый': 972075663,
            'ярко-зеленый': 972075590,
            'ярко-красный': 972075571,
            'ярко-розовый': 972075536,
            'ярко-салатовый': 972075921,
            'ярко-синий': 972075567
        }
        colors_russian = list(color_vals.keys())
        for arr in (colors_russian, colors_english):
            for color in arr:
                if color in x:
                    if color in color_vals:
                        self.color_id = color_vals[color]
                    return color

    def brand_detector(self, x) -> str:
        dirr = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dirr, 'json/brands.json'), 'r', encoding='utf-8') as f:
            brands = json.load(f)
        for brand in brands:
            if brand.lower() in x.lower():
                self.brand_id = brands[brand]
                return brand

    def parse_data_from_name(self, x):
        self.type = self.type_detector(x)
        self.brand = self.brand_detector(x)
        self.color = self.color_detector(x)
        for sub in (self.raw_type, self.color, self.brand):
            if sub is None:
                continue
            x = x.replace(sub, '')
        self.short = self.cleaner(x)
        self.find_ids(self.type)

    def find_ids(self, item_type: str):
        dirr = os.path.dirname(os.path.realpath(__file__))
        _df = pd.read_excel(os.path.join(dirr, 'xls/ozon_categories.xlsx'))
        if not item_type:
            cats_df = _df[_df['main'] == 'Электроника']
            c = cats_df['child'].to_list()
            self.type = random.choice(c)
            item_type = self.type
        r = _df[_df['child'] == item_type]
        for i, row in r.iterrows():
            self.main_category_id = row.get('main_category_id')
            self.description_category_id = row.get('sub_category_id')
            self.type_id = row.get('child_id')


class Ozon:
    def __init__(
            self,
            client_id: str,
            api_key: str,
            nomenclature: Optional[list[Nomenclature]] = None,
            warehouse_id: Optional[int] = None
    ):
        """
        Описаны основные методы для работы с озон, сделаны максимально похожими как у яндекса
        :param client_id: Айди кабинета
        :param api_key:
        :param nomenclature: Готовая номенклатура для выгрузки на МП
        :param warehouse_id: Айди склада на который грузим
        """
        self.headers = {'Client-Id': client_id, 'Api-Key': api_key}
        self.warehouse_id = warehouse_id
        self.base_url = "https://api-seller.ozon.ru/"
        self.items = nomenclature
        self.name = "Озон"

    def offers_list(self, items_list: Optional[list] = None, last_id: Optional[int] = None) -> list[OfferItem]:
        items_list: list[OfferItem] = items_list or []
        url = self.base_url + "v2/product/list"
        response = OzonResponse(
            requests.post(url,
                          headers=self.headers,
                          json={
                              "filter": {
                                  "visibility": ozon_types.VisibilityType.ALL,
                              },
                              "last_id": last_id or "",
                              "limit": 1000
                          }
                          ).json()
        )
        if response.result:
            page = OffersPaginationResponse(response.result)
            items_list.extend(page.items)
            if page.last_id:
                self.offers_list(items_list=items_list, last_id=page.last_id)
        else:
            print(response.message, response.details, response.code)
        response = OzonResponse(
            requests.post(url,
                          headers=self.headers,
                          json={
                              "filter": {
                                  "visibility": ozon_types.VisibilityType.ARCHIVED,
                              },
                              "last_id": last_id or "",
                              "limit": 1000
                          }
                          ).json()
        )
        items_list.extend(OffersPaginationResponse(response.result).items)
        return items_list

    def market_items(self) -> list[DataOzonItem]:
        url = self.base_url + "v2/product/info/list"
        l = self.offers_list()
        offer_ids = [t.offer_id for t in l]
        results_list = []
        if len(offer_ids) > 1000:
            for arr in split_arrs(offer_ids, 1000):
                req = requests.post(url,
                                    headers=self.headers,
                                    json={
                                        "offer_id": to_json(arr)
                                    }
                                    )
                try:
                    response = OzonResponse(
                        req.json()
                    )
                except Exception as e:
                    raise e
                if response.result:
                    results_list.extend([DataOzonItem(t) for t in response.result.get("items")])
                else:
                    print(response.message, response.details, response.code)
        else:
            response = OzonResponse(
                requests.post(url,
                              headers=self.headers,
                              json={
                                  "offer_id": to_json(offer_ids)
                              }
                              ).json()
            )
            if response.result:
                results_list.extend([DataOzonItem(t) for t in response.result.get("items")])
            else:
                print(response.message, response.details, response.code)
        return results_list

    def warehouses_list(self) -> list[Warehouse]:
        url = self.base_url + "v1/warehouse/list"
        response = OzonResponse(
            requests.post(url,
                          headers=self.headers
                          ).json()
        )
        if response.result:
            return [Warehouse(w) for w in response.result]
        else:
            print(response.message, response.details)

    def create_items(self) -> tuple[list[CreateItemInfo], int] | tuple[None, None]:
        url = self.base_url + "v3/product/import"
        market_items = self.offers_list()
        items_to_create = []
        for n in self.items:
            if n.article not in [o.offer_id for o in market_items] and n.ozon_price:
                atrbts = ItemInfo(n.name)
                _create = dict(
                    offer_id=n.article,
                    description_category_id=atrbts.description_category_id,
                    price=str(n.ozon_price),
                    name=n.name,
                    barcode=n.barcode or "",
                    height=250,
                    depth=20,
                    weight=300,
                    width=20,
                    currency_code=ozon_types.CurrencyType.RUB,
                    dimension_unit=ozon_types.DimensionUnitType.MM,
                    vat=ozon_types.ItemVatType.VAT_0,
                    weight_unit=ozon_types.WeightUnitType.g,
                    images=n.pictures or [],
                    primary_image="",
                    attributes=[
                        {  # бренд
                            "complex_id": 0,
                            "id": 85,
                            "values": [
                                {
                                    "dictionary_value_id": atrbts.brand_id,
                                    "value": atrbts.brand,
                                }
                            ]
                        },
                        {  # тип товара
                            "complex_id": 0,
                            "id": 8229,
                            "values": [
                                {
                                    "dictionary_value_id": atrbts.type_id,
                                    "value": atrbts.type
                                }
                            ]
                        },
                        {  # название товара без бренда, цвета, типа
                            "complex_id": 0,
                            "id": 9048,
                            "values": [
                                {
                                    "value": atrbts.short
                                }
                            ]
                        },
                        {  # цвет товара
                            "complex_id": 0,
                            "id": 10096,
                            "values": [
                                {
                                    "dictionary_value_id": atrbts.color_id or 61574,
                                    "value": atrbts.color or 'черный'
                                }
                            ]
                        }
                    ],
                    complex_attributes=[],
                    images360=[],
                    pdf_list=[],
                )
                items_to_create.append(_create)
        tasks = []
        result = []
        if not items_to_create:
            return None, None
        if items_to_create:
            if len(items_to_create) > 100:
                for arr in split_arrs(items_to_create, 100):
                    response = OzonResponse(
                        requests.post(url,
                                      headers=self.headers,
                                      json={"items": arr}
                                      ).json()
                    )
                    if response.result:
                        tasks.append(response.result.get("task_id"))
                    else:
                        print(response.message, response.details, response.code)
            else:
                response = OzonResponse(
                    requests.post(url,
                                  headers=self.headers,
                                  json={"items": items_to_create}
                                  ).json()
                )
                if response.result:
                    tasks.append(response.result.get("task_id"))
                else:
                    print(response.message, response.details, response.code)
            pprint.pprint(tasks)
            url = self.base_url + "v1/product/import/info"
            for task in tasks:
                req = requests.post(url,
                                    headers=self.headers,
                                    json={"task_id": task})
                response = OzonResponse(req.json())
                if response.result:
                    result.extend(CreateItemResponse(response.result).items)
                else:
                    print(response.message, response.details, response.code)
        return result, len(items_to_create)

    def task_info(self, tasks: list):
        url = self.base_url + "v1/product/import/info"
        result = []
        for task in tasks:
            req = requests.post(url,
                                headers=self.headers,
                                json={"task_id": task})
            response = OzonResponse(req.json())
            if response.result:
                result.extend(CreateItemResponse(response.result).items)
            else:
                print(response.message, response.details, response.code)
        return result

    def update_price(self) -> list[OzonResponse]:
        url = self.base_url + "v1/product/import/prices"
        prices = [
            UpdatePriceItem(
                price=str(n.ozon_price),
                offer_id=n.article,
                auto_action_enabled=ozon_types.EnabledType.UNKNOWN,
                currency_code=ozon_types.CurrencyType.RUB,
                price_strategy_enabled=ozon_types.EnabledType.UNKNOWN
            ) for n in self.items if n.ozon_price
        ]
        response_list = []
        if len(prices) > 100:
            for arr in split_arrs(prices, 100):
                response = OzonResponse(
                    requests.post(url,
                                  headers=self.headers,
                                  json={
                                      "prices": to_json(arr)
                                  }
                                  ).json()
                )
                if response.result:
                    response_list.append(response)
                else:
                    print(response.message, response.details, response.code)
        else:
            response = OzonResponse(
                requests.post(url,
                              headers=self.headers,
                              json={
                                  "prices": to_json(prices)
                              }
                              ).json()
            )
            if response.result:
                response_list.append(response)
            else:
                print(response.message, response.details, response.code)
        return response_list

    def update_stocks(self) -> list[StocksResponse]:
        url = self.base_url + "v2/products/stocks"
        stoks_update = []
        articles = []
        update_info = []
        for n in self.items:
            stoks_update.append(
                UpdateStockItem(
                    offer_id=n.article,
                    stock=n.stock if n.ozon_category else 0,
                    warehouse_id=self.warehouse_id,
                )
            )
            articles.append(n.article)
        for t in self.market_items():
            if t.offer_id not in articles:
                stoks_update.append(
                    UpdateStockItem(
                        offer_id=t.offer_id,
                        stock=0,
                        warehouse_id=self.warehouse_id,
                    )
                )
        if len(stoks_update) > 100:
            for arr in split_arrs(stoks_update, 100):
                req = requests.post(url,
                                    headers=self.headers,
                                    json={
                                        "stocks": to_json(arr)
                                    }
                                    )
                response = OzonResponse(req.json())
                if response.result:
                    update_info.extend([StocksResponse(r) for r in response.result])

                else:
                    print(response.message, response.details, response.code)
        else:
            response = OzonResponse(
                requests.post(url,
                              headers=self.headers,
                              json={
                                  "stocks": to_json(stoks_update)
                              }
                              ).json()
            )
            if response.result:
                update_info.extend([StocksResponse(r) for r in response.result])
            else:
                print(response.message, response.details, response.code)
        return update_info

    def orders(self) -> list[OzonOrder]:
        url = self.base_url + "v3/posting/fbs/list"
        cur = datetime.now()
        ago = datetime.now() - timedelta(days=7)
        req = requests.post(url,
                          headers=self.headers,
                          json=to_json(
                              PostingGetter(
                                  _dir=ozon_types.SortDirectionType.DESC,
                                  _filter=FilterOrders(
                                      since=f"{ago.strftime("%Y-%m-%d")}T00:00:00Z",
                                      to=f"{cur.strftime("%Y-%m-%d")}T23:59:59.59Z"
                                  ),
                                  limit=20,
                                  offset=0,
                              )
                          )
                          ).json()
        response = OzonResponse(req)
        if response.result:
            return PostingResponsePadding(response.result).postings
        else:
            print(response.message, response.details, response.code)

    def attributies(self):
        url = self.base_url + "v3/products/info/attributes"
        return OzonResponse(requests.post(url,
                                          headers=self.headers,
                                          json={
                                              "filter": {"visibility": "ALL"},
                                              "limit": 1000
                                          },
                                          ).json())

    def categories(self) -> list[Category]:
        url = self.base_url + "v1/description-category/tree"
        return [Category(c) for c in requests.post(url, headers=self.headers).json().get('result')]

    def category_atributies(self, description_category_id, type_id):
        url = self.base_url + "v1/description-category/attribute"
        resp = requests.post(url,
                             headers=self.headers,
                             json={
                                 'description_category_id': description_category_id,
                                 'type_id': type_id
                             }
                             )
        return OzonResponse(resp.json())

    def desc_category_atributies(self, atr_id, category_id, type_id, last_v=None):
        url = self.base_url + "v1/description-category/attribute/values"
        resp = requests.post(url,
                             headers=self.headers,
                             json={
                                 "attribute_id": atr_id,
                                 "description_category_id": category_id,
                                 "language": "DEFAULT",
                                 "limit": 5,
                                 "type_id": type_id,
                                 "last_value_id": last_v or 0,
                             }
                             )
        return OzonResponse(resp.json())

    def limits(self):
        url = "https://api-seller.ozon.ru/v4/product/info/limit"
        resp = requests.post(url, headers=self.headers)
        return resp.json()


def to_json(obj: Any, style: bool = False, save_null=False) -> Any:
    """
    Создаем из любого кастомного объекта словарь, где ключ это переменные объекта, а значения - значение переменной
    :param style:
    :param obj:
    :return:
    """
    replacer = lambda s: ''.join(c.upper() if i > 0 and s[i - 1] == '_' else c for i, c in enumerate(s) if c != '_')
    if isinstance(obj, dict):
        result = {}
        for key, val in obj.items():
            if val is not None:
                result[replacer(key) if style else key] = to_json(val)
        return result
    elif isinstance(obj, list):
        return [to_json(t) for t in obj if t is not None]
    elif hasattr(obj, '__dict__'):
        return {replacer(k) if style else k: to_json(v) for k, v in obj.__dict__.items()
                if v is not None and not save_null}
    else:
        return obj


split_arrs = lambda arr, rang: [arr[i:i + rang] for i in range(0, len(arr), rang)]
