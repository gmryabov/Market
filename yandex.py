"""
Объекты взяты с оф.документации Яндекс Маркет
https://yandex.ru/dev/market/partner-api/doc/ru/api/
"""

import re
from main import yandex_types
import requests
from typing import Optional
from main.custom_classes import Nomenclature


class OrderItemPromo:
    def __init__(self, order_promo):
        self.type: yandex_types.OrderPromoType = order_promo.get("type")
        self.discount: float = order_promo.get("discount")
        self.subsidy: float = order_promo.get("subsidy")
        self.shop_promo_id: str = order_promo.get("shop_promo_id")
        self.market_promo_id: str = order_promo.get("market_promo_id")


class OrderItemInstance:
    def __init__(self, _instances):
        self.cis: str = _instances.get("cis")
        self.cis_full: str = _instances.get("cis_full")
        self.uin: str = _instances.get("uin")
        self.rnpt: str = _instances.get("rnpt")
        self.gtd: str = _instances.get("gtd")


class OrderItemDetail:
    def __init__(self, _item_detail):
        self.item_count: int = _item_detail.get("item_count")
        self.item_status: yandex_types.OrderItemStatusType = _item_detail.get("item_status")
        self.update_date: str = _item_detail.get("update_date")


class OrderItemSubsidy:
    def __init__(self, _subsidy):
        self.type: yandex_types.OrderItemSubsidyType = _subsidy.get("type")
        self.amount: float = _subsidy.get("amount")


class OrderItem:
    def __init__(self, _item: dict):
        self.id: int = _item.get("id")
        self.offer_id: str = _item.get("offerId")
        self.offer_name: str = _item.get("offerName")
        self.price: float = _item.get("price")
        self.buyer_price: float = _item.get("buyerPrice")
        self.buyer_price_before_discount: float = _item.get("buyerPriceBeforeDiscount")
        self.parther_warehouse_id: int = _item.get("partnerWarehouseId")
        self.count: str = _item.get("count")
        self.promos: list[OrderItemPromo] = [OrderItemPromo(pr) for pr in _item.get("promos")] \
            if _item.get("promos") else None
        self.required_instance_types: yandex_types.OrderItemInstanceType = _item.get("requiredInstanceTypes")
        self.vat: yandex_types.OrderVatType = _item.get("vat")


class OrderCourier:
    def __init__(self, _courier):
        self.full_name: str = _courier.get("fullName")
        self.phone: str = _courier.get("phone")
        self.phone_extension: str = _courier.get("phoneExtension")
        self.vehicle_number: str = _courier.get("vehicleNumber")
        self.vehicle_description: str = _courier.get("vehicleDescription")


class OrderDeliveryDates:
    def __init__(self, _delivery_dates):
        self.from_date: str = _delivery_dates.get("fromDate")
        self.to_date: str = _delivery_dates.get("toDate")
        self.from_time: str = _delivery_dates.get("fromTime")
        self.to_time: str = _delivery_dates.get("toTime")
        self.real_delivery_date: str = _delivery_dates.get("realDeliveryDate")


class Region:
    def __init__(self, _region):
        self.id: int = _region.get("id")
        self.name: str = _region.get("name")
        self.type: yandex_types.RegionType = _region.get("type")
        self.parent: Region = Region(_region.get("parent"))
        self.children: Region = Region(_region.get("children"))


class OrderTrackDTO:
    def __init__(self, _track_dto):
        self.track_code: str = _track_dto.get("trackCode")
        self.delivery_service_id: int = _track_dto.get("deliveryServiceId")


class OrderParcelBoxDTO:
    def __init__(self, _parcel_box_dto):
        self.id: int = _parcel_box_dto.get("id")
        self.fulfilment_id: str = _parcel_box_dto.get("fulfilmentId")


class OrderShipmentDTO:
    def __init__(self, _shipment_dto):
        self.id = _shipment_dto.get("id")
        self.shipment_date: str = _shipment_dto.get("shipmentDate")
        self.shipment_time: str = _shipment_dto.get("shipmentTime")
        self.track: OrderTrackDTO = OrderTrackDTO(_shipment_dto.get("track")) if _shipment_dto.get("track") else None
        self.boxes: OrderParcelBoxDTO = OrderParcelBoxDTO(_shipment_dto.get("parcelBox")) \
            if _shipment_dto.get("parcelBox") else None


class OrderDelivery:
    def __init__(self, order_delivery):
        self.id: str = order_delivery.get("id")
        self.type: yandex_types.OrderDeliveryType = order_delivery.get("type")
        self.service_name: str = order_delivery.get("service_name")  # Наименование службы доставки
        # Тип сотрудничества со службой доставки в рамках конкретного заказа.
        self.delivery_partner_type: str = order_delivery.get("delivery_partner_type")
        self.courier: OrderCourier = order_delivery.get("courier")
        self.dates: OrderDeliveryDates = OrderDeliveryDates(order_delivery.get("dates"))  # Диапазон дат доставки.
        self.region: Region = order_delivery.get("region")
        self.address: OrderDeliveryAddress = OrderDeliveryAddress(order_delivery.get("address"))
        self.vat: yandex_types.OrderVatType = order_delivery.get("vat")
        self.delivery_service_id: yandex_types.OrderLiftType = order_delivery.get("deliveryServiceId")
        self.delivery_partner_type: yandex_types.OrderDeliveryPartnerType = order_delivery.get("deliveryPartnerType")
        self.lift_price: float = order_delivery.get("liftPrice")
        self.outlet_code: str = order_delivery.get("outlet_code")
        self.outlet_storage_limit_date: str = order_delivery.get("outletStorageLimitDate")
        self.dispatch_type: yandex_types.OrderDeliveryDispatchType = order_delivery.get("dispatchType")
        self.tracks: OrderTrackDTO = OrderTrackDTO(order_delivery.get("tracks")) \
            if order_delivery.get("tracks") else None
        self.shipments = [OrderShipmentDTO(ship) for ship in order_delivery.get("shipments")]
        self.estimated: bool = order_delivery.get("estimated")
        self.eac_type: yandex_types.OrderDeliveryEacType = order_delivery.get("eac_type")
        self.eac_code: str = order_delivery.get("eacCode")  # Код подтверждения ЭАПП (для типа MERCHANT_TO_COURIER)


class Gps:
    def __init__(self, _gps):
        self.latitude: float = _gps.get("latitude")
        self.longitude: float = _gps.get("longitude")


class OrderDeliveryAddress:
    def __init__(self, _address):
        self.country: str = _address.get("country")
        self.postcode: str = _address.get("postcode")
        self.city: str = _address.get("city")
        self.district: str = _address.get("district")
        self.subway: str = _address.get("subway")
        self.street: str = _address.get("street")
        self.house: str = _address.get("house")
        self.block: str = _address.get("block")
        self.entrance: str = _address.get("entrance")
        self.entryphone: str = _address.get("entryphone")
        self.floor: str = _address.get("floor")
        self.apartment: str = _address.get("apartment")
        self.recipient: str = _address.get("recipient")
        self.gps: Gps = Gps(_address.get("gps"))
        self.phone: str = _address.get("phone")


class OrderBuyer:
    def __init__(self, _buyer):
        self.id: str = _buyer.get("id")
        self.last_name: str = _buyer.get("lastName")
        self.first_name: str = _buyer.get("firstName")
        self.middle_name: str = _buyer.get("middleName")
        self.type: yandex_types.OrderBuyerType = _buyer.get("type")


class YandexOrder:
    def __init__(self, raw_data):
        self.id: int = raw_data.get("id")
        self.creation_date: str = raw_data.get("creationDate")
        self.currency: yandex_types.CurrencyType = raw_data.get("currency")
        self.status: yandex_types.OrderStatusType = raw_data.get("status")
        self.substatus: yandex_types.OrderSubstatusType = raw_data.get("substatus")
        self.items_total: float = raw_data.get("itemsTotal")
        self.delivery_total: float = raw_data.get("deliveryTotal")
        self.buyer_items_total: float = raw_data.get("buyerItemsTotal")
        self.buyer_items_total_before_discount: float = raw_data.get("buyerTotalBeforeDiscount")
        self.buyer_total_before_discount: float = raw_data.get("buyerTotalBeforeDiscount")
        self.payment_type: yandex_types.OrderPaymentType = raw_data.get("paymentType")
        self.payment_method: yandex_types.OrderPaymentMethodType = raw_data.get("paymentMethod")
        self.fake: bool = raw_data.get("fake")
        self.items: list[OrderItem] = [OrderItem(item) for item in raw_data.get("items")]
        self.subsidies: list[OrderItemSubsidy] = [OrderItemSubsidy(sub) for sub in raw_data.get("subsidies")] \
            if raw_data.get("subsidies") else None
        self.delivery: OrderDelivery = OrderDelivery(raw_data.get("delivery"))
        self.buyer: OrderBuyer = OrderBuyer(raw_data.get("buyer"))
        self.notes: str = raw_data.get("notes")
        self.tax_system: yandex_types.OrderTaxSystemType = raw_data.get("taxSystem")
        self.cancel_requested: bool = raw_data.get("cancelRequested")
        self.expiry_date: str = raw_data.get("expiryDate")

    def __str__(self):
        text = f"*Номер заказа:* `{self.id}`\n"
        text += f"*Дата:* {self.creation_date}\n"
        true_status = {
            "CANCELLED": "🚫 Отменен",
            "DELIVERED": "✅ Получен покупателем",
            "DELIVERY": "🚚 Передан в службу доставки",
            "PICKUP": "🚚 Доставлен в пункт самовывоза",
            "PROCESSING": "⏳ Находится в обработке",
            "PENDING": "⏳ Ожидает обработки со стороны продавца",
            "UNPAID": "⚡️ Оформлен, но еще не оплачен (если выбрана оплата при оформлении)",
            "PLACING": "⚡️ Оформляется, подготовка к резервированию",
            "RESERVED": "📦 Зарезервирован, но недооформлен",
            "PARTIALLY_RETURNED": "🟠 Возвращен частично",
            "RETURNED": "🚫 Возвращен полностью",
            "UNKNOWN": "❔Неизвестный статус",
        }

        delivery_true = {
            "DELIVERY": "курьерская доставка",
            "PICKUP": "самовывоз",
            "POST": "почта",
            "DIGITAL": "для цифровых товаров",
            "UNKNOWN": "неизвестный тип",
        }

        text += f"*Статус:* {true_status.get(self.status)}\n"
        text += f"*Состав заказа:* \n`{'`\n`'.join([p.offer_name for p in self.items])}`\n"
        text += f"*Сумма заказа:* {self.items_total}\n"
        text += f"*Способ доставки:* {delivery_true.get(str(self.delivery.type))}\n"
        text += f"*Клиент:* {self.buyer.first_name or ""} {self.buyer.last_name or ""}\n"
        text += f"*Адрес:* `{address(self.delivery.address.__dict__)}`"
        return text


def address(x) -> str:
    text = ""
    for k, v in x.items():
        if k == "gps":
            continue
        if k in ['country', 'city', 'district', 'subway', 'street', 'postcode']:
            text = (text + f"{v} ") if v else text
        else:
            replace = {"house": "дом",
                       "entrance": "подъезд",
                       "entryphone": "домофон",
                       "floor": "этаж",
                       "apartment": "квартира",
                       "recipient": "получатель",
                       "phone": "телефон"}
            text = (text + f"{replace.get(k)} {v} ") if v else text
    return text


class BusinessDTO:
    def __init__(self, business_dto):
        self.id: int = business_dto.get("id")
        self.name: str = business_dto.get("name")


class CampaignDTO:
    def __init__(self, campaign_dto):
        self.domain: str = campaign_dto.get("domain")
        self.id: int = campaign_dto.get("id")
        self.client_id: int = campaign_dto.get("clientId")
        self.business: BusinessDTO = BusinessDTO(campaign_dto.get("business"))
        self.placement_type: yandex_types.PlacementType = campaign_dto.get("placementType")


class FlippingPagerDTO:
    def __init__(self, flipping_dto):
        self.total: int = flipping_dto.get("total")
        self._from: int = flipping_dto.get("from")
        self.to: int = flipping_dto.get("to")
        self.current_page: int = flipping_dto.get("currentPage")
        self.pages_count: int = flipping_dto.get("pagesCount")


class OfferManualDTO:
    def __init__(self, url: str, title: str):
        self.url = url
        self.title = title


class OfferWeightDimensionsDTO:
    def __init__(self, length: float, width: float, height: float, weight: float):
        self.length: float = length
        self.width: float = width
        self.height: float = height
        self.weight: float = weight


class TimePeriodDTO:
    def __init__(self, time_period: str, time_unit: yandex_types.TimeUnitType, comment: str):
        self.time_period = time_period
        self.time_unit = time_unit
        self.comment = comment


class OfferConditionDTO:
    def __init__(self, __type: yandex_types.OfferConditionType, quality: yandex_types.OfferConditionQualityType,
                 reason: str):
        self.type = __type
        self.quality = quality
        self.reason = reason


class AgeDTO:
    def __init__(self, age_dto):
        self.value: float = age_dto.get("value")
        self.age_unit: yandex_types.AgeUniType = age_dto.get("ageUnit")


class ParameterValueDTO:
    def __init__(self, parameter_value_dto):
        self.parameter_id: int = parameter_value_dto.get("parameterId")
        self.unit_id: int = parameter_value_dto.get("unitId")
        self.value_id: int = parameter_value_dto.get("valueId")
        self.value: str = parameter_value_dto.get("value")


class UpdatePriceWithDiscountDTO:
    def __init__(self,
                 value: float,
                 currency_id: yandex_types.CurrencyType,
                 discount_base: Optional[float] = None):
        self.value: float = value
        self.currency_id: yandex_types.CurrencyType = currency_id
        self.discount_base: float = discount_base


class BasePriceDTO:
    def __init__(self,
                 value: float,
                 currency_id: yandex_types.CurrencyType):
        self.value = value
        self.currency_id = currency_id


class UpdateMappingDTO:
    def __init__(self, market_sku: int = None):
        self.market_sku = market_sku

    def __str__(self):
        return str(self.market_sku)


class UpdateOfferDTO:
    def __init__(
            self,
            offer_id: str,
            name: str,
            category: str,
            pictures: list[str],
            description: str,
            vendor_code: str,
            purchase_price: BasePriceDTO,
            basic_price: Optional[UpdatePriceWithDiscountDTO] = None,
            market_category_id: Optional[int] = None,
            videos: Optional[str] = None,
            mauals: Optional[OfferManualDTO] = None,
            vendor: Optional[str] = None,
            manufacturer_countries: Optional[str] = None,
            weight_dimensions: Optional[OfferWeightDimensionsDTO] = None,
            tags: Optional[str] = None,
            shelf_life: Optional[TimePeriodDTO] = None,
            life_time: Optional[TimePeriodDTO] = None,
            guarantee_period: Optional[TimePeriodDTO] = None,
            customs_commodity_code: Optional[str] = None,
            certificates: Optional[str] = None,
            box_count: Optional[int] = None,
            condition: Optional[OfferConditionDTO] = None,
            _type: Optional[yandex_types.OfferType] = None,
            downloadable: Optional[bool] = None,
            adult: Optional[bool] = None,
            age: Optional[AgeDTO] = None,
            parameter_values: Optional[ParameterValueDTO] = None,
            additional_expenses: Optional[BasePriceDTO] = None,
            cofinance_price: Optional[BasePriceDTO] = None
    ) -> None:
        self.offer_id = offer_id
        self.name = name
        self.market_category_id = market_category_id
        self.category = category
        self.pictures = pictures
        self.videos = videos
        self.mauals = mauals
        self.vendor = vendor
        self.description = description
        self.manufacturer_countries = manufacturer_countries
        self.weight_dimensions = weight_dimensions
        self.vendor_code = vendor_code
        self.tags = tags
        self.shelf_life = shelf_life
        self.life_time = life_time
        self.guarantee_period = guarantee_period
        self.customs_commodity_code = customs_commodity_code
        self.certificates = certificates
        self.box_count = box_count
        self.condition = condition
        self.type = _type
        self.downloadable = downloadable
        self.adult = adult
        self.age = age
        self.parameter_values = parameter_values
        # Цена на товар.
        self.basic_price = basic_price
        # Себестоимость
        self.purchase_price = purchase_price
        # Дополнительные расходы на товар.
        self.additional_expenses = additional_expenses
        # Цена для скидок с Маркетом.
        self.cofinance_price = cofinance_price

    def __str__(self):
        return str(self.__dict__)


class UpdateOfferMappingDTO:
    def __init__(self, _items: list[Nomenclature]):
        _parser = lambda x: x.split("-")[-1]  # парсинг категории
        self.offer_mappings = [
            dict(
                offer=UpdateOfferDTO(
                    offer_id=_item.article,
                    name=_item.name,
                    category=_parser(_item.yandex_category),
                    market_category_id=_item.site_category_id,
                    pictures=_item.pictures,
                    description=_item.description,
                    vendor_code=_item.article,
                    purchase_price=BasePriceDTO(value=_item.yandex_price,
                                                currency_id=yandex_types.CurrencyType.RUR),
                    vendor=_item.vendor,
                ),
                mapping=UpdateMappingDTO()
            )
            for _item in _items]

    def __str__(self):
        return str(self.__dict__)

    def __len__(self):
        return len(self.offer_mappings)


class GetPriceWithDiscount:
    def __init__(self, get_price_with_discont: dict):
        self.value = get_price_with_discont.get('value')
        self.currency_id: yandex_types.CurrencyType = get_price_with_discont.get('currency_id')
        self.discount_base: float = get_price_with_discont.get('discountBase')
        self.updated_at: str = get_price_with_discont.get('updatedAt')


class GetPriceDTO:
    def __init__(self, get_price_dto: dict):
        self.value = get_price_dto.get('value')
        self.currency_id: yandex_types.CurrencyType = get_price_dto.get('currency_id')
        self.updated_at: str = get_price_dto.get('updatedAt')


class OfferCampaignStatus:
    def __init__(self, offer_campaign_status: dict):
        self.offer_campaign_status = [dict(
            campaignId=o.get("campaignId"),
            status=o.get("status"))
            for o in offer_campaign_status]


class OfferSellingProgramDTO:
    def __init__(self, offer_selling: dict):
        self.offer_selling = [dict(sellingProgram=o.get('sellingProgram'),
                                   status=o.get('status'))
                              for o in offer_selling]


class GetOfferDTO:
    def __init__(self, get_offer):
        self.offer_id: str = get_offer.get("offerId")
        self.name: str = get_offer.get("name")
        self.market_category_id: int = get_offer.get("marketCategoryId")
        self.category: str = get_offer.get("category")
        self.pictures: list[str] = get_offer.get("pictures")
        self.videos: list[str] = get_offer.get("videos")
        self.mauals: OfferManualDTO = get_offer.get("mauals")
        self.vendor: str = get_offer.get("vendor")
        self.description: str = get_offer.get("description")
        self.manufacturer_countries: list[str] = get_offer.get("manufacturerCountries")
        self.barcodes: list[str] = get_offer.get("barcodes")
        self.weight_dimensions: OfferWeightDimensionsDTO = get_offer.get("weightDimensions")
        self.vendor_code: str = get_offer.get("vendorCode")
        self.tags: list[str] = get_offer.get("tags")
        self.shelf_life: TimePeriodDTO = get_offer.get("shelfLife")
        self.life_time: TimePeriodDTO = get_offer.get("lifeTime")
        self.guarantee_period: TimePeriodDTO = get_offer.get("guaranteePeriod")
        self.customs_commodity_code: str = get_offer.get("customsCommodityCode")
        self.certificates: list[str] = get_offer.get("certificates")
        self.box_count: int = get_offer.get("boxCount")
        self.condition: OfferConditionDTO = get_offer.get("condition")
        self.type: yandex_types.OfferType = get_offer.get("type")
        self.downloadable: bool = get_offer.get("downloadable")
        self.adult: bool = get_offer.get("adult")
        self.age: AgeDTO = AgeDTO(get_offer.get("age")) if "age" in get_offer else None
        # Цена на товар.
        self.basic_price: GetPriceWithDiscount = GetPriceWithDiscount(get_offer.get("basicPrice")) \
            if "basicPrice" in get_offer else None
        # Себестоимость
        self.purchase_price = GetPriceDTO(get_offer.get("purchasePrice")) if "purchasePrice" in get_offer else None
        # Дополнительные расходы на товар.
        self.additional_expenses: GetPriceDTO = GetPriceDTO(get_offer.get("additionalExpenses")) \
            if "additionalExpenses" in get_offer else None
        # Цена для скидок с Маркетом.
        self.cofinance_price = GetPriceDTO(get_offer.get("cofinancePrice")) \
            if "cofinancePrice" in get_offer else None
        self.card_status: yandex_types.OfferCardStatusType = get_offer.get("cardStatus")
        self.campaigns = OfferCampaignStatus(get_offer.get("campaigns")) if "campaigns" in get_offer else None
        self.selling_programs = OfferSellingProgramDTO(get_offer.get("sellingPrograms")) \
            if "sellingPrograms" in get_offer else None
        self.archived: bool = get_offer.get("archived")


class ScrollingPagerDTO:
    def __init__(self, scrolling_pager_dto: dict):
        self.next_page_token = scrolling_pager_dto.get("nextPageToken")
        self.prev_page_token = scrolling_pager_dto.get("prevPageToken")


class GetOfferMappingDTO:
    def __init__(self, offer_mapping_dto: list[dict]):
        self.offer_mapping = [
            dict(
                offer=GetOfferDTO(data.get("offer")),
                mapping=GetMappingDTO(data.get("mapping")),
            ) for data in offer_mapping_dto if "mapping" in data
        ]


class GetMappingDTO:
    def __init__(self, get_mapping: dict):
        self.market_sku: int = get_mapping.get("marketSku")
        self.market_sku_name: str = get_mapping.get("marketSkuName")
        self.market_model_id: int = get_mapping.get("marketModelId")
        self.market_model_name: str = get_mapping.get("marketModelName")
        self.market_category_id: int = get_mapping.get("marketCategoryId")
        self.market_category_name: str = get_mapping.get("marketCategoryName")


class GetOfferMappingsResultDTO:
    def __init__(self, _result: dict):
        self.paging: ScrollingPagerDTO = ScrollingPagerDTO(_result.get("paging"))
        self.offer_mapings: GetOfferMappingDTO = GetOfferMappingDTO(_result.get("offerMappings"))


class YandexResponse:
    def __init__(self, response: dict):
        self.status: yandex_types.ApiResponseStatusType = response.get("status")
        self.result: GetOfferMappingsResultDTO = GetOfferMappingsResultDTO(response.get("result"))


class UpdateBusinessOfferPriceDTO:
    def __init__(self,
                 offer_id: str,
                 price: UpdatePriceWithDiscountDTO,
                 ):
        self.offer_id = offer_id
        self.price = price


class PriceDTO:
    def __init__(self,
                 currency_id: yandex_types.CurrencyType,
                 value: float,
                 discount_base: Optional[float] = None,
                 vat: Optional[int] = None):
        """
        Vat
        2 — 10%.
        5 — 0%.
        6 — не облагается НДС.
        7 — 20%.
        :param currency_id:
        :param value:
        :param discount_base:
        :param vat:
        """
        self.currency_id = currency_id
        self.discount_base = discount_base
        self.value = value
        self.vat = vat


class OfferPriceDTO:
    def __init__(self, offer_id: str, price: PriceDTO):
        self.offer_id = offer_id
        self.price = price


class UpdateStockItemDTO:
    def __init__(self, count: int, updated_at: str = None):
        """
        Дата и время последнего обновления информации об остатках.
        Если вы не передали параметр updatedAt, используется текущее время.
        Формат даты и времени: ISO 8601 со смещением относительно UTC. Например, 2017-11-21T00:42:42+03:00.
        """
        self.count = count
        self.updated_at = updated_at


class UpdateStockDTO:
    def __init__(self, sku: str, items: list[UpdateStockItemDTO]):
        self.sku = sku
        self.items = items


class YandexMarket:
    def __init__(self,
                 token: str,
                 client_id: int,
                 nomenclature: Optional[list[Nomenclature]] = None,
                 campaign_id: Optional[int] = None,
                 ):
        """
        Клиент для взаимодействия с МП, схож с озон
        :param token:
        :param client_id:
        :param nomenclature:
        :param campaign_id:
        """
        self.headers = {"Authorization": token}
        self.business_id = client_id
        self.base_url = "https://api.partner.market.yandex.ru/"
        if nomenclature:
            self.items = [n for n in nomenclature if valid(n.article) and n.yandex_category and n.yandex_price]
        self.campaign_id = campaign_id
        self.name = "Яндекс Маркет"

    def warehouses_list(self, query_params: Optional[dict] = None) -> dict:
        resp = requests.get(f"{self.base_url}campaigns",
                            headers=self.headers,
                            params=query_params or {}
                            ).json()
        return {"campaigns": [CampaignDTO(c) for c in resp.get("campaigns")],
                "pager": FlippingPagerDTO(resp.get("pager"))}

    def orders(self, query_params: Optional[dict] = None) -> list[YandexOrder]:
        response = requests.get(f"{self.base_url}campaigns/{self.campaign_id}/orders",
                                headers=self.headers,
                                params=query_params or {"pageSize": 20}
                                ).json()
        return [YandexOrder(_or) for _or in response.get("orders")][:20]

    def order(self, order_id: int) -> YandexOrder:
        url = self.base_url + f"campaigns/{self.campaign_id}/orders/{order_id}"
        response = requests.get(url, headers=self.headers).json()
        return YandexOrder(response.get('order'))

    def create_items(self) -> tuple:
        url = f"{self.base_url}businesses/{self.business_id}/offer-mappings/update"

        market_items = self.market_items()
        uplodet = [of.offer_id for of in market_items]
        items_to_create = [n for n in self.items if n.article not in uplodet]
        if not items_to_create:
            return None, None
        result = []
        if len(items_to_create) > 500:
            for arr in split_arrs(items_to_create, 500):
                req = requests.post(url,
                                    headers=self.headers,
                                    json=to_json(UpdateOfferMappingDTO(arr), style=True))
                result.append(req)
        else:
            result.append(
                requests.post(url,
                              headers=self.headers,
                              json=to_json(UpdateOfferMappingDTO(items_to_create), style=True))
            )
        return result, len(items_to_create)

    def market_items(
            self,
            query_params: Optional[dict] = None,
            filter_params: Optional[dict] = None,
            market_items: Optional[list] = None
    ) -> list[GetOfferDTO]:
        market_items = market_items or []
        url = f"{self.base_url}businesses/{self.business_id}/offer-mappings"
        req = requests.post(url,
                            headers=self.headers,
                            json=filter_params or
                                 {
                                     "archived": False
                                 },
                            params=query_params
                                   or
                                   {
                                       "limit": 200,
                                       "page_token": ""
                                   }
                            )
        response = YandexResponse(req.json())
        market_items.extend(response.result.offer_mapings.offer_mapping)
        if response.status == yandex_types.ApiResponseStatusType.OK and response.result.paging.next_page_token:
            self.market_items(query_params={
                "limit": 200,
                "page_token": response.result.paging.next_page_token,
            }, market_items=market_items)
        return [m.get('offer') for m in market_items]

    def update_price(self) -> None:
        url = self.base_url + f"businesses/{self.business_id}/offer-prices/updates"
        url_campaining = self.base_url + f"campaigns/{self.campaign_id}/offer-prices/updates"
        list_basic_prices = []
        list_campaign_prices = []
        for n in self.items:
            list_basic_prices.append(
                UpdateBusinessOfferPriceDTO(
                    offer_id=n.article,
                    price=UpdatePriceWithDiscountDTO(
                        value=n.yandex_price,
                        currency_id=yandex_types.CurrencyType.RUR
                    )
                )
            )
            list_campaign_prices.append(
                OfferPriceDTO(
                    offer_id=n.article,
                    price=PriceDTO(
                        currency_id=yandex_types.CurrencyType.RUR,
                        value=n.yandex_price,
                        vat=6,
                    )
                )
            )

        if len(self.items) > 500:
            for arr in split_arrs(list_basic_prices, 500):
                requests.post(url, headers=self.headers, json={"offers": to_json(arr, style=True)})
            for arr in split_arrs(list_campaign_prices, 500):
                requests.post(url_campaining, headers=self.headers, json={"offers": to_json(arr, style=True)})
        else:
            requests.post(url, headers=self.headers, json={"offers": to_json(list_basic_prices)})
            requests.post(url_campaining,
                          headers=self.headers,
                          json={"offers": to_json(list_campaign_prices, style=True)})

    def update_stocks(self) -> None:
        url = self.base_url + f"campaigns/{self.campaign_id}/offers/stocks"
        stock_list = []
        articles = []
        mrkt = self.market_items()
        for n in self.items:
            stock_list.append(
                UpdateStockDTO(
                    sku=n.article,
                    items=[
                        UpdateStockItemDTO(
                            count=n.stock
                            if (n.yandex_price and n.yandex_category and n.yandex_category) else 0)
                    ]
                )
            )
            articles.append(n.article)
        for t in mrkt:
            _item: GetOfferDTO = t
            if _item.offer_id not in articles:
                stock_list.append(
                    UpdateStockDTO(
                        sku=_item.offer_id,
                        items=[UpdateStockItemDTO(count=0)]
                    )
                )
        if len(stock_list) > 2000:
            for arr in split_arrs(stock_list, 2000):
                requests.put(url, headers=self.headers, json={"skus": to_json(arr, style=True)})
        else:
            requests.put(url, headers=self.headers, json={"skus": to_json(stock_list, style=True)})


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


split_arrs = lambda arr, rang: [arr[i:i + rang] for i in range(0, len(arr), rang)]
valid = lambda x: re.findall("^[0-9a-zа-яА-ЯA-ZёËëЁ.,\\\\/()\\[\\]\\-=_]{1,80}$", x)
