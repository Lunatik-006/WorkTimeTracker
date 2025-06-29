TRANSLATIONS = {
    "en": {},
    "ru": {
        "Pomodoro Timer": "Таймер Помодоро",
        "Open": "Настройки",
        "Timers": "Таймеры",
        "+ New Timer": "+ Новый таймер",
        "Name": "Название",
        "Description": "Описание",
        "Sets": "Подходы",
        "Rest between activities": "Отдых между активностями",
        "Rest between sets": "Отдых между подходами",
        "Activities": "Активности",
        "Add activity": "Добавить активность",
        "Save": "Сохранить",
        "Cancel": "Отмена",
        "Invalid name": "Неверное имя",
        "Name must be 1-50 characters: letters, digits, spaces, '_' or '-'": "Имя должно быть 1-50 символов: буквы, цифры, пробелы, '_' или '-'",
        "Invalid description": "Неверное описание",
        "Description must be less than 200 characters": "Описание должно быть меньше 200 символов",
        "Limit": "Лимит",
        "Maximum 25 activities per timer": "Максимум 25 активностей на таймер",
        "Unsaved changes": "Несохраненные изменения",
        "у вас есть несохраненные изменения": "У вас есть несохраненные изменения",
        "Delete": "Удалить",
        "Timer": "Таймер",
        "Timer: {name}": "Таймер: {name}",
        "All sets completed": "Все подходы завершены",
        "Rest": "Отдых",
        "Rest between sets": "Отдых между подходами",
        "Start": "Старт",
        "Pause": "Пауза",
        "Stop": "Стоп",
        "Next": "Далее",
        "Settings": "Настройки",
        "Application language": "Язык приложения",
        "Speech language": "Язык озвучки",
        "Voice": "Голос",
        "Notification sound": "Вид звуковых оповещений",
        "None": "Нет",
        "Beep": "Писк",
        "Horn": "Гудок",
        "VoiceTTS": "Озвучка",
        "OK": "OK",
        "timer started": "таймер запущен",
        "timer stopped": "таймер остановлен",
        "rest": "отдых",
        "Timer name delete confirm": "Вы действительно хотите удалить таймер '{name}'?",
        "Set {current}/{total}: {activity}": "Сет {current}/{total}: {activity}",
        "Activity": "Активность",
        "Duration": "Длительность",
    },
    "cn": {}
}

_current_lang = "en"
_callbacks = []

def set_language(lang: str):
    global _current_lang
    _current_lang = lang
    for cb in list(_callbacks):
        try:
            cb()
        except Exception:
            pass

def get_language():
    return _current_lang


def register(callback):
    if callback not in _callbacks:
        _callbacks.append(callback)

def unregister(callback):
    if callback in _callbacks:
        _callbacks.remove(callback)

def tr(text: str) -> str:
    return TRANSLATIONS.get(_current_lang, {}).get(text, text)
