from datetime import datetime, timedelta
import re

filename_ds="DeepAssistTime"
filename_flows="FLOWS time"
# Читаем новый файл
with open(f"C:\\Users\\fded3\\Desktop\\{filename_flows}.txt", encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines()]

# Найдём индекс строки с "ОПЛАЧЕНО"
last_paid_index = max(i for i, line in enumerate(lines) if 'ОПЛАЧЕНО' in line)

# Обрезаем строки после "ОПЛАЧЕНО"
post_paid_lines = lines[last_paid_index + 1:]

date_pattern = re.compile(r'\d{4}\.\d{2}\.\d{2}')
time_pattern = re.compile(r'\d{1,2}:\d{2}')

current_date = None
current_block_times = []
total_minutes = 0
block_start_date = None
block_end_date = None

i = 0
while i < len(post_paid_lines):
    line = post_paid_lines[i]

    # Обнаружена дата
    if date_pattern.match(line):
        current_date = line
        if block_start_date is None:
            block_start_date = current_date
        block_end_date = current_date
        i += 1
        continue

    # Начало блока временных меток
    if time_pattern.match(line):
        block_times = []
        # Пока не пустая строка и не дата — собираем метки
        while i < len(post_paid_lines) and post_paid_lines[i] and not date_pattern.match(post_paid_lines[i]):
            times = time_pattern.findall(post_paid_lines[i])
            block_times.extend(times)
            i += 1

        # Если есть хотя бы 2 метки — считаем интервал
        if len(block_times) >= 2:
            t1 = datetime.strptime(block_times[0], '%H:%M')
            t2 = datetime.strptime(block_times[-1], '%H:%M')
            delta = (t2 - t1).total_seconds() / 60
            # Если время пошло "через полночь", корректируем
            if delta < 0:
                delta += 24 * 60
            total_minutes += delta
    else:
        i += 1

# Округление до 0.5 часа
total_hours = round(total_minutes / 30) / 2

result = f"{total_hours} часов (с {block_start_date} по {block_end_date})"
print(result)