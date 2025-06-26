PAID = "ОПЛАЧЕНО"
INVOICED = "СЧЕТ ВЫСТАВЛЕН"
UNPAID = "ДЕНЕГ НЕТ"

import os

import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_LOG_DIR = os.path.join(BASE_DIR, "projects")

DATE_PATTERN = re.compile(r"\d{4}\.\d{2}\.\d{2}")
TIME_PATTERN = re.compile(r"\d{1,2}:\d{2}")
