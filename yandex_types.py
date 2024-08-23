class OrderStatusType:
    CANCELLED = "CANCELLED"  # отменен
    DELIVERED = "DELIVERED"  # получен покупателем
    DELIVERY = "DELIVERY"  # передан в службу доставки
    PICKUP = "PICKUP"  # доставлен в пункт самовывоза
    PROCESSING = "PROCESSING"  # находится в обработке
    PENDING = "PENDING"  # ожидает обработки со стороны продавца
    UNPAID = "UNPAID"  # оформлен, но еще не оплачен (если выбрана оплата при оформлении)
    PLACING = "PLACING"  # оформляется, подготовка к резервированию
    RESERVED = "RESERVED"  # зарезервирован, но недооформлен
    PARTIALLY_RETURNED = "PARTIALLY_RETURNED"  # возвращен частично
    RETURNED = "RETURNED"  # возвращен полностью
    UNKNOWN = "UNKNOWN"  # неизвестный статус



class OrderSubstatusType:
    # для статуса PROCESSING
    STARTED = "STARTED"  # заказ подтвержден, его можно начать обрабатывать
    READY_TO_SHIP = "READY_TO_SHIP"  # заказ собран и готов к отправке
    # для статуса CANCELLED
    PROCESSING_EXPIRED = "PROCESSING_EXPIRED"  # значение более не используется
    REPLACING_ORDER = "REPLACING_ORDER"  # покупатель решил заменить товар другим по собственной инициативе
    # покупатель не завершил оформление зарезервированного заказа в течение 10 минут
    RESERVATION_EXPIRED = "RESERVATION_EXPIRED"
    SHOP_FAILED = "SHOP_FAILED"  # магазин не может выполнить заказ
    USER_CHANGED_MIND = "USER_CHANGED_MIND"  # покупатель отменил заказ по личным причинам
    USER_NOT_PAID = "USER_NOT_PAID"  # покупатель не оплатил заказ (для типа оплаты PREPAID) в течение 30 минут
    USER_REFUSED_DELIVERY = "USER_REFUSED_DELIVERY"  # покупателя не устроили условия доставки
    USER_REFUSED_PRODUCT = "USER_REFUSED_PRODUCT"  # покупателю не подошел товар
    USER_REFUSED_QUALITY = "USER_REFUSED_QUALITY"  # покупателя не устроило качество товара
    USER_UNREACHABLE = "USER_UNREACHABLE"  # не удалось связаться с покупателем.


class OrderDeliveryDispatchType:
    BUYER = "BUYER"  # доставка покупателю
    MARKET_PARTNER_OUTLET = "MARKET_PARTNER_OUTLET"  # доставка в пункт выдачи партнера
    MARKET_BRANDED_OUTLET = "MARKET_BRANDED_OUTLET"  # доставка в пункт выдачи заказов Маркета
    SHOP_OUTLET = "SHOP_OUTLET"  # доставка в пункт выдачи заказов магазина
    DROPOFF = "DROPOFF"  # доставка в пункт выдачи, который принимает заказы от продавцов и передает их курьерам
    UNKNOWN = "UNKNOWN"  # неизвестный тип


class OrderBuyerType:
    PERSON = "PERSON"  # физическое лицо
    BUSINESS = "BUSINESS"  # организация


class CurrencyType:
    BYR = "BYR"  # белорусский рубль
    KZT = "KZT"  # казахстанский тенге
    RUR = "RUR"  # российский рубль
    UAH = "UAH"  # украинская гривна


class OrderPaymentType:
    PREPAID = "PREPAID"  # оплата при оформлении заказа
    POSTPAID = "POSTPAID"  # оплата при получении заказа
    UNKNOWN = "UNKNOWN"  # неизвестный тип


class OrderPaymentMethodType:
    # Значения, если выбрана оплата при оформлении заказа ("paymentType": "PREPAID"):
    YANDEX = "YANDEX"  # банковской картой
    APPLE_PAY = "APPLE_PAY"  # Apple Pay
    GOOGLE_PAY = "GOOGLE_PAY"  # Google Pay
    CREDIT = "CREDIT"  # в кредит
    TINKOFF_CREDIT = "TINKOFF_CREDIT"  # в кредит в Тинькофф Банке
    TINKOFF_INSTALLMENTS = "TINKOFF_INSTALLMENTS"  # рассрочка в Тинькофф Банке
    EXTERNAL_CERTIFICATE = "EXTERNAL_CERTIFICATE"  # подарочным сертификатом (например, из приложения «Сбербанк Онлайн»)
    SBP = "SBP"  # через систему быстрых платежей
    B2B_ACCOUNT_PREPAYMENT = "B2B_ACCOUNT_PREPAYMENT"  # заказ оплачивает организация
    # Значения, если выбрана оплата при получении заказа ("paymentType": "POSTPAID"):
    CARD_ON_DELIVERY = "CARD_ON_DELIVERY"  # банковской картой
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"  # наличными
    B2B_ACCOUNT_POSTPAYMENT = "B2B_ACCOUNT_POSTPAYMENT"  # заказ оплачивает организация после доставки
    UNKNOWN = "UNKNOWN"  # неизвестный тип


class OrderVatType:
    # НДС не облагается, используется только для отдельных видов услуг.
    # НДС 0%. Например, используется при продаже товаров, вывезенных в таможенной процедуре экспорта,
    # или при оказании услуг по международной перевозке товаров.
    NO_VAT = "NO_VAT"
    VAT_0 = "VAT_0"
    # НДС 10%. Например, используется при реализации отдельных продовольственных и медицинских товаров.
    VAT_10 = "VAT_10"
    # НДС 10/110. Расчетная ставка НДС 10%, применяется только при предоплате.
    VAT_10_110 = "VAT_10_110"
    # НДС 20%. Основная ставка с 2019 года.
    VAT_20 = "VAT_20"
    # НДС 20/120. Расчетная ставка НДС 20%, применяется только при предоплате.
    VAT_20_120 = "VAT_20_120"
    # НДС 18%. Основная ставка до 2019 года.
    VAT_18 = "VAT_18"
    # НДС 18/118. Ставка использовалась до 1 января 2019 года при предоплате.
    VAT_18_118 = "VAT_18_118"
    # неизвестный тип.
    UNKNOWN_VALUE = "UNKNOWN_VALUE"


class OrderPromoType:
    DIRECT_DISCOUNT = "DIRECT_DISCOUNT"  # прямая скидка, которую устанавливает продавец или Маркет.
    BLUE_SET = "BLUE_SET"  # комплекты.
    BLUE_FLASH = "BLUE_FLASH"  # флеш-акция.
    MARKET_COUPON = "MARKET_COUPON"  # скидка по промокоду Маркета.
    MARKET_PROMOCODE = "MARKET_PROMOCODE"  # скидка по промокоду магазина.
    MARKET_BLUE = "MARKET_BLUE"  # скидка на Маркете.
    YANDEX_PLUS = "YANDEX_PLUS"  # бесплатная доставка с подпиской Яндекс Плюс.
    YANDEX_EMPLOYEE = "YANDEX_EMPLOYEE"  # бесплатная доставка по определенным адресам.
    LIMITED_FREE_DELIVERY_PROMO = "LIMITED_FREE_DELIVERY_PROMO"  # бесплатная доставка по ограниченному предложению.
    FREE_DELIVERY_THRESHOLD = "FREE_DELIVERY_THRESHOLD"  # бесплатная доставка при достижении определенной суммы заказа.
    MULTICART_DISCOUNT = "MULTICART_DISCOUNT"  # скидка за то, что оформлена мультикорзина.
    FREE_DELIVERY_FOR_LDI = "FREE_DELIVERY_FOR_LDI"  # бесплатная доставка за то, что один из товаров крупногабаритный.
    # бесплатная доставка за то, что одна из корзин в мультикорзине крупногабаритная.
    FREE_DELIVERY_FOR_LSC = "FREE_DELIVERY_FOR_LSC"
    FREE_PICKUP = "FREE_PICKUP"  # бесплатная доставка в пункт выдачи заказов.
    CHEAPEST_AS_GIFT = "CHEAPEST_AS_GIFT"  # самый дешевый товар в подарок.
    CASHBACK = "CASHBACK"  # кешбэк.
    SUPPLIER_MULTICART_DISCOUNT = "SUPPLIER_MULTICART_DISCOUNT"  # скидка за доставку.
    SPREAD_DISCOUNT_COUNT = "SPREAD_DISCOUNT_COUNT"  # скидка за количество одинаковых товаров.
    SPREAD_DISCOUNT_RECEIPT = "SPREAD_DISCOUNT_RECEIPT"  # скидка от суммы чека.
    ANNOUNCEMENT_PROMO = "ANNOUNCEMENT_PROMO"  # информационная акция, скидка не применяется к товарам.
    DISCOUNT_BY_PAYMENT_TYPE = "DISCOUNT_BY_PAYMENT_TYPE"  # прямая скидка при оплате картой Плюса.
    PERCENT_DISCOUNT = "PERCENT_DISCOUNT"  # прямая скидка в процентах.
    DCO_EXTRA_DISCOUNT = "DCO_EXTRA_DISCOUNT"  # дополнительная скидка, необходимая для расчета субсидии от Маркета.
    EMPTY_PROMO = "EMPTY_PROMO"  # скрытые промокоды.
    BLOCKING_PROMO = "BLOCKING_PROMO"  # блокирующее промо.
    UNKNOWN = "UNKNOWN"  # неизвестный тип.


class OrderItemStatusType:
    REJECTED = "REJECTED"  # невыкупленный
    RETURNED = "RETURNED"  # возвращенный


class OrderItemInstanceType:
    CIS = "CIS"  # КИЗ, идентификатор единицы товара в системе «Честный ЗНАК»
    UIN = "UIN"  # УИН, уникальный идентификационный номер
    RNPT = "RNPT"  # РНПТ, регистрационный номер партии товара
    GTD = "GTD"  # номер ГТД, грузовой таможенной декларации


class OrderItemSubsidyType:
    YANDEX_CASHBACK = "YANDEX_CASHBACK"  # скидка по подписке Яндекс Плюс
    SUBSIDY = "SUBSIDY"  # скидка Маркета (по акциям, промокодам, купонам и т. д.).


class OrderDeliveryType:
    DELIVERY = "DELIVERY"  # курьерская доставка
    PICKUP = "PICKUP"  # самовывоз
    POST = "POST"  # почта
    DIGITAL = "DIGITAL"  # для цифровых товаров
    UNKNOWN = "UNKNOWN"  # неизвестный тип



class OrderDeliveryPartnerType:
    SHOP = "SHOP"  # магазин работает со службой доставки напрямую или доставляет заказы самостоятельно
    YANDEX_MARKET = "YANDEX_MARKET"  # магазин работает со службой доставки через Маркет
    UNKNOWN = "UNKNOWN"  # неизвестный тип


class RegionType:
    CITY_DISTRICT = "CITY_DISTRICT"  # район города
    CITY = "CITY"  # крупный город
    CONTINENT = "CONTINENT"  # континент
    COUNTRY_DISTRICT = "COUNTRY_DISTRICT"  # область
    COUNTRY = "COUNTRY"  # страна
    REGION = "REGION"  # регион
    REPUBLIC_AREA = "REPUBLIC_AREA"  # район субъекта федерации
    REPUBLIC = "REPUBLIC"  # субъект федерации
    SUBWAY_STATION = "SUBWAY_STATION"  # станция метро
    VILLAGE = "VILLAGE"  # город
    OTHER = "OTHER"  # неизвестный регион


class OrderDeliveryEacType:
    MERCHANT_TO_COURIER = "MERCHANT_TO_COURIER"  # продавец передает код курьеру
    COURIER_TO_MERCHANT = "COURIER_TO_MERCHANT"  # курьер передает код продавцу
    CHECKING_BY_MERCHANT = "CHECKING_BY_MERCHANT"  # продавец проверяет код на своей стороне


class OrderTaxSystemType:
    ECHN = "ECHN"  # единый сельскохозяйственный налог (ЕСХН).
    ENVD = "ENVD"  # единый налог на вмененный доход (ЕНВД).
    OSN = "OSN"  # общая система налогообложения (ОСН).
    PSN = "PSN"  # патентная система налогообложения (ПСН).
    USN = "USN"  # упрощенная система налогообложения (УСН).
    # упрощенная система налогообложения, доходы, уменьшенные на величину расходов (УСН «Доходы минус расходы»).
    USN_MINUS_COST = "USN_MINUS_COST"
    NPD = "NPD"  # налог на профессиональный доход (НПД).
    # Неизвестное значение. Используется только совместно с параметром payment-method=YANDEX
    UNKNOWN_VALUE = "UNKNOWN_VALUE"


class PlacementType:
    FBS = "FBS"  # или Экспресс.
    FBY = "FBY"
    DBS = "DBS"


class TimeUnitType:
    HOUR = "HOUR"  # час.
    DAY = "DAY"  # сутки.
    WEEK = "WEEK"  # неделя.
    MONTH = "MONTH"  # месяц.
    YEAR = "YEAR"  # год.


class OfferConditionType:
    PREOWNED = "PREOWNED"  # бывший в употреблении товар, раньше принадлежал другому человеку.
    SHOWCASESAMPLE = "SHOWCASESAMPLE"  # витринный образец.
    REFURBISHED = "REFURBISHED"  # повторная продажа товара.
    REDUCTION = "REDUCTION"  # товар с дефектами.
    RENOVATED = "RENOVATED"  # восстановленный товар.
    NOT_SPECIFIED = "NOT_SPECIFIED"  # не выбран.


class OfferConditionQualityType:
    PERFECT = "PERFECT"  # идеальный.
    EXCELLENT = "EXCELLENT"  # отличный.
    GOOD = "GOOD"  # хороший.
    NOT_SPECIFIED = "NOT_SPECIFIED"  # не выбран.


class OfferType:
    MEDICINE = "MEDICINE"  # лекарства.
    BOOK = "BOOK"  # бумажные и электронные книги.
    AUDIOBOOK = "AUDIOBOOK"  # аудиокниги.
    ARTIST_TITLE = "ARTIST_TITLE"  # музыкальная и видеопродукция.
    ON_DEMAND = "ON_DEMAND"  # товары на заказ


class AgeUniType:
    YEAR = "YEAR"
    MONTH = "MONTH"


class OfferCardStatusType:
    HAS_CARD_CAN_NOT_UPDATE = "HAS_CARD_CAN_NOT_UPDATE"  # Карточка Маркета.
    HAS_CARD_CAN_UPDATE = "HAS_CARD_CAN_UPDATE"  # Можно дополнить.
    HAS_CARD_CAN_UPDATE_ERRORS = "HAS_CARD_CAN_UPDATE_ERRORS"  # Изменения не приняты.
    HAS_CARD_CAN_UPDATE_PROCESSING = "HAS_CARD_CAN_UPDATE_PROCESSING"  # Изменения на проверке.
    NO_CARD_NEED_CONTENT = "NO_CARD_NEED_CONTENT"  # Создайте карточку.
    NO_CARD_MARKET_WILL_CREATE = "NO_CARD_MARKET_WILL_CREATE"  # Создаст Маркет.
    NO_CARD_ERRORS = "NO_CARD_ERRORS"  # Не создана из-за ошибки.
    NO_CARD_PROCESSING = "NO_CARD_PROCESSING"  # Проверяем данные.
    NO_CARD_ADD_TO_CAMPAIGN = "NO_CARD_ADD_TO_CAMPAIGN"  # Разместите товар в магазине.


class OrderLiftType:
    NOT_NEEDED = "NOT_NEEDED"  # не требуется.
    MANUAL = "MANUAL"  # ручной.
    ELEVATOR = "ELEVATOR"  # лифт.
    CARGO_ELEVATOR = "CARGO_ELEVATOR"  # грузовой лифт.
    FREE = "FREE"  # любой из перечисленных выше, если включена опция бесплатного подъема.
    UNKNOWN = "UNKNOWN"  # неизвестный тип.


class OfferCampaignStatusType:
    PUBLISHED = "PUBLISHED"  # Готов к продаже.
    CHECKING = "CHECKING"  # На проверке.
    DISABLED_BY_PARTNER = "DISABLED_BY_PARTNER"  # Скрыт вами.
    REJECTED_BY_MARKET = "REJECTED_BY_MARKET"  # Отклонен.
    DISABLED_AUTOMATICALLY = "DISABLED_AUTOMATICALLY"  # Исправьте ошибки.
    CREATING_CARD = "CREATING_CARD"  # Создается карточка.
    NO_CARD = "NO_CARD"  # Нужна карточка.
    NO_STOCKS = "NO_STOCKS"  # Нет на складе.


class SellingProgramType:
    """Модель размещения."""
    FBY = "FBY"
    FBS = "FBS"
    DBS = "DBS"
    EXPRESS = "EXPRESS"


class OfferSellingProgramStatusType:
    """Информация о том, можно ли по этой модели продавать товар."""
    FINE = "FINE"
    REJECT = "REJECT"


class ApiResponseStatusType:
    OK = "OK"
    ERROR = "ERROR"
