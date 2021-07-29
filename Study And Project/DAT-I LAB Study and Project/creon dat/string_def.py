class QueStr:
    DATA = "data"
    ORDER = "order"
    COM = "com"
    MAIN = "main"
    STG = "strategy"
    ST = "stock"


class DataBase:
    USR = "DB_ID"
    PWD = "DB_PWD"
    URL = "DB_IP"
    PORT = "DB_PORT"
    DB = "DB_NAME"


class Server:
    MCAST_GRP = "SERVER_GRP"
    IF_IP = "SERVER_IF_IP"
    PORT = "SERVER_PORT"


class TradeType:
    BID = "bid"
    ASK = "ask"


class InitParam:
    """
    # init json format
        "strategy"
        "balance"
        "manage_funds"
        "manage_weights"
    """
    STG = "strategy"
    BAL = "balance"
    MNG_FUND = "manage_funds"
    MNG_WGHT = "manage_weights"


class DataName:
    # --- Data ---
    DATA    = "data"
    RT_TICK = "rt_tick"
    RT_QUOTE = "rt_quote"
    RT_CHART = "rt_chart"
    SPOT    = "spot"
    CHART   = "chart"
    BALANCE = "balance"
    # --- Cp Conclusion ---
    CCLN    = "conclusion"
    RT_CCLN = "rt_conclusion"


class Interval:
    SEC = "s"
    MIN = "m"
    HOUR = "h"
    DAY = "d"
    TICK = "t"


class StgSetting:
    STRATEGYID = ""
    STOCKS = []
    TDUNIT = 60
    INTERVAL = 0
    NUMBARS = 0


class InvestorCode:
    FNTLINVTR = 1000
    INSURANCE = 2000
    ASSETMANAGE = 3000
    PRVEQTY = 3100
    BANK = 4000
    PENSION = 6000
    NOTRATED = 7000
    ETCCORP = 7100
    PERSONAL = 8000
    FOREIGNWID = 9000
    FOREIGNWOID = 9001
    ETC = 5000


class Trnd:
    STANDSTILL = 0
    RISING = -1
    FALLING = 1


class OrdType:
    NEW = 1
    MDY = 2
    CNCL = 3

