"""
Типы используемые для работы с озон
"""


class VisibilityType:
    ALL = "ALL"  # все товары, кроме архивных.
    VISIBLE = "VISIBLE"  # товары, которые видны покупателям.
    INVISIBLE = "INVISIBLE"  # товары, которые не видны покупателям.
    EMPTY_STOCK = "EMPTY_STOCK"  # товары, у которых не указано наличие.
    NOT_MODERATED = "NOT_MODERATED"  # товары, которые не прошли модерацию.
    MODERATED = "MODERATED"  # товары, которые прошли модерацию.
    DISABLED = "DISABLED"  # товары, которые видны покупателям, но недоступны к покупке.
    STATE_FAILED = "STATE_FAILED"  # товары, создание которых завершилось ошибкой.
    READY_TO_SUPPLY = "READY_TO_SUPPLY"  # товары, готовые к поставке.
    # товары, которые проходят проверку валидатором на премодерации.
    VALIDATION_STATE_PENDING = "VALIDATION_STATE_PENDING"
    VALIDATION_STATE_FAIL = "VALIDATION_STATE_FAIL"  # товары, которые не прошли проверку валидатором на премодерации.
    # товары, которые прошли проверку валидатором на премодерации.
    VALIDATION_STATE_SUCCESS = "VALIDATION_STATE_SUCCESS"
    TO_SUPPLY = "TO_SUPPLY"  # товары, готовые к продаже.
    IN_SALE = "IN_SALE"  # товары в продаже.
    REMOVED_FROM_SALE = "REMOVED_FROM_SALE"  # товары, скрытые от покупателей.
    BANNED = "BANNED"  # заблокированные товары.
    OVERPRICED = "OVERPRICED"  # товары с завышенной ценой.
    CRITICALLY_OVERPRICED = "CRITICALLY_OVERPRICED"  # товары со слишком завышенной ценой.
    EMPTY_BARCODE = "EMPTY_BARCODE"  # товары без штрихкода.
    BARCODE_EXISTS = "BARCODE_EXISTS"  # товары со штрихкодом.
    QUARANTINE = "QUARANTINE"  # товары на карантине после изменения цены более чем на 50%.
    ARCHIVED = "ARCHIVED"  # товары в архиве.
    OVERPRICED_WITH_STOCK = "OVERPRICED_WITH_STOCK"  # товары в продаже со стоимостью выше, чем у конкурентов.
    PARTIAL_APPROVED = "PARTIAL_APPROVED"  # товары в продаже с пустым или неполным описанием.
    IMAGE_ABSENT = "IMAGE_ABSENT"  # товары без изображений.
    MODERATION_BLOCK = "MODERATION_BLOCK"  # товары, для которых заблокирована модерация.


class CurrencyType:
    RUB = "RUB"  # российский рубль
    BYN = "BYN"  # белорусский рубль
    KZT = "KZT"  # тенге
    EUR = "EUR"  # евро
    USD = "USD"  # доллар США
    CNY = "CNY"  # юань


class DimensionUnitType:
    MM = "mm"  # миллиметры
    CM = "cm"  # сантиметры
    IN = "in"  # дюймы


class ItemServiceType:
    IS_CODE_SERVICE = "IS_CODE_SERVICE"
    IS_NO_CODE_SERVICE = "IS_NO_CODE_SERVICE"


class ItemVatType:
    """
    VAT_0 не облагается НДС
    VAT_10 - 10%
    VAT_20 - 20%
    """
    VAT_0 = "0"
    VAT_10 = "0.1"
    VAT_20 = "0.2"


class WeightUnitType:
    g = "g"  # граммы
    kg = "kg"  # килограммы
    lb = "lb"  # фунты


class PriceIndexType:
    WITHOUT_INDEX = "WITHOUT_INDEX"  # без индекса,
    PROFIT = "PROFIT"  # выгодный,
    AVG_PROFIT = "AVG_PROFIT"  # умеренный,
    NON_PROFIT = "NON_PROFIT"  # невыгодный.


class EnabledType:
    ENABLED = "ENABLED"  # включить
    DISABLED = "DISABLED"  # выключить
    UNKNOWN = "UNKNOWN"  # ничего не менять, передаётся по умолчанию


class PostingStatusType:
    awaiting_registration = "awaiting_registration"  # ожидает регистрации
    acceptance_in_progress = "acceptance_in_progress"  # идёт приёмка
    awaiting_approve = "awaiting_approve"  # ожидает подтверждения
    awaiting_packaging = "awaiting_packaging"  # ожидает упаковки
    awaiting_deliver = "awaiting_deliver"  # ожидает отгрузки
    awaiting_verification = "awaiting_verification"  # создано
    arbitration = "arbitration"  # арбитраж
    client_arbitration = "client_arbitration"  # клиентский арбитраж доставки
    cancelled_from_split_pending = "cancelled_from_split_pending"  # отменён из-за разделения отправления
    delivering = "delivering"  # доставляется
    driver_pickup = "driver_pickup"  # у водителя
    delivered = "delivered"  # доставлено
    cancelled = "cancelled"  # отменено
    not_accepted = "not_accepted"  # не принят на сортировочном центре
    sent_by_seller = "sent_by_seller"  # отправлено продавцом


class PostingSubStatusType:
    posting_acceptance_in_progress = "posting_acceptance_in_progress"  # идёт приёмка
    posting_in_arbitration = "posting_in_arbitration"  # арбитраж
    posting_created = "posting_created"  # создано
    posting_in_carriage = "posting_in_carriage"  # в перевозке
    posting_not_in_carriage = "posting_not_in_carriage"  # не добавлено в перевозку
    posting_registered = "posting_registered"  # зарегистрировано
    posting_transferring_to_delivery = "posting_transferring_to_delivery"  # передаётся в доставку
    posting_awaiting_passport_data = "posting_awaiting_passport_data"  # ожидает паспортных данных
    posting_awaiting_registration = "posting_awaiting_registration"  # ожидает регистрации
    posting_registration_error = "posting_registration_error"  # ошибка регистрации
    posting_split_pending = "posting_split_pending"  # создано
    posting_canceled = "posting_canceled"  # отменено
    posting_in_client_arbitration = "posting_in_client_arbitration"  # клиентский арбитраж доставки
    posting_delivered = "posting_delivered"  # доставлено
    posting_received = "posting_received"  # получено
    posting_conditionally_delivered = "posting_conditionally_delivered"  # условно доставлено
    posting_in_courier_service = "posting_in_courier_service"  # курьер в пути
    posting_in_pickup_point = "posting_in_pickup_point"  # в пункте выдачи
    posting_on_way_to_city = "posting_on_way_to_city"  # в пути в ваш город
    posting_on_way_to_pickup_point = "posting_on_way_to_pickup_point"  # в пути в пункт выдачи
    posting_returned_to_warehouse = "posting_returned_to_warehouse"  # возвращено на склад
    posting_transferred_to_courier_service = "posting_transferred_to_courier_service"  # передаётся в службу доставки
    posting_driver_pick_up = "posting_driver_pick_up"  # у водителя
    posting_not_in_sort_center = "posting_not_in_sort_center"  # не принято на сортировочном центре
    sent_by_seller = "sent_by_seller"  # отправлено продавцом


class SortDirectionType:
    ASC = "asc"
    DESC = "desc"


class PaymentType:
    CARD = "картой онлайн"
    OZON_CARD = "Ozon Карта"
    SBP = "Система Быстрых Платежей"
    OZON_CREDIT = "Ozon Рассрочка"
    SberPay = "SberPay"
    CHECK = "оплата на расчётный счёт"
    SAVE_CARD = "сохранённой картой при получении"


class CancellationInitiatorType:
    Client = "Клиент"
    Ozon = "Ozon"
    Seller = "Продавец"


class CancellationType:
    client = "client"  # клиентская.
    ozon = "ozon"  # отменено Ozon.
    seller = "seller"  # отменено продавцом.


class TplIntegrationType:
    """Тип интеграции со службой доставки"""
    ozon = "ozon"  # доставка службой Ozon
    pl_tracking = "3pl_tracking"  # доставка интегрированной службой
    non_integrated = "non_integrated"  # доставка сторонней службой
    aggregator = "aggregator"  # доставка через партнёрскую доставку Ozon
    hybryd = "hybryd"  # схема доставки Почты России


class PrrOptionType:
    lift = "lift"  # подъём на лифте
    stairs = "stairs"  # подъём по лестнице
    none = "none"  # покупатель отказался от услуги, поднимать товары не нужно
    delivery_default = "delivery_default"  # доставка включена в стоимость


class CreateStatusType:
    pending = "pending"  # товар в очереди на обработку
    imported = "imported"  # товар успешно загружен
    failed = "failed"  # товар загружен с ошибками
