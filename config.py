from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

EXCEL_FILE_NAME = "Cars price.xlsx"
DATABASE_FILE_NAME = "customers.db"

EXCEL_PATH = BASE_DIR / EXCEL_FILE_NAME
DATABASE_PATH = BASE_DIR / DATABASE_FILE_NAME

WHATSAPP_NUMBER = "+7 707 102 4666"

FIRST_RATE = 0.15
SECOND_RATE = 0.16

CUSTOMS_COLLECTION = 25_950
SBKTS_EPTS_FEE = 400_000
BROKER_SERVICE_FEE = 300_000

QUOTE_VALID_DAYS = 7

BRAND_CHINESE_NAMES = {
    "ACURA": "讴歌",
    "AITO": "问界",
    "ARCFOX": "极狐",
    "ASTON MARTIN": "阿斯顿·马丁",
    "AUDI": "奥迪",
    "AVATR": "阿维塔",
    "BENTLEY": "宾利",
    "BMW": "宝马",
    "BYD": "比亚迪",
    "CADILLAC": "凯迪拉克",
    "CHANGAN": "长安",
    "CHERY": "奇瑞",
    "CHEVROLET": "雪佛兰",
    "CHRYSLER": "克莱斯勒",
    "CITROEN": "雪铁龙",
    "DODGE": "道奇",
    "EXEED": "星途",
    "FERRARI": "法拉利",
    "FORD": "福特",
    "GEELY": "吉利",
    "GENESIS": "捷尼赛思",
    "GMC": "GMC",
    "GREAT WALL": "长城",
    "HAVAL": "哈弗",
    "HONDA": "本田",
    "HONGQI": "红旗",
    "HYUNDAI": "现代",
    "INFINITI": "英菲尼迪",
    "JAGUAR": "捷豹",
    "JEEP": "吉普",
    "KIA": "起亚",
    "LAMBORGHINI": "兰博基尼",
    "LAND ROVER": "路虎",
    "LEAPMOTOR": "零跑",
    "LEXUS": "雷克萨斯",
    "LINCOLN": "林肯",
    "LOTUS": "路特斯",
    "MASERATI": "玛莎拉蒂",
    "MAZDA": "马自达",
    "MCLAREN": "迈凯伦",
    "MERCEDES-BENZ": "奔驰",
    "MERCEDES BENZ": "奔驰",
    "MERCEDES": "奔驰",
    "BENZ": "奔驰",
    "MINI": "迷你",
    "MITSUBISHI": "三菱",
    "NISSAN": "日产",
    "PEUGEOT": "标致",
    "PORSCHE": "保时捷",
    "RAM": "道奇公羊",
    "RENAULT": "雷诺",
    "ROLLS-ROYCE": "劳斯莱斯",
    "SUBARU": "斯巴鲁",
    "SUZUKI": "铃木",
    "TESLA": "特斯拉",
    "TOYOTA": "丰田",
    "VOLKSWAGEN": "大众",
    "VOLVO": "沃尔沃",
    "XPENG": "小鹏",
    "ZEEKR": "极氪",
}
