PAID = "ОПЛАЧЕНО"
INVOICED = "СЧЕТ ВЫСТАВЛЕН"

import re
DATE_PATTERN = re.compile(r"\d{4}\.\d{2}\.\d{2}")
TIME_PATTERN = re.compile(r"\d{1,2}:\d{2}")
