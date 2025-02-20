import telebot
import requests
import re
import time
from telebot import types
from datetime import datetime

# Создаем Telegram-бота
bot = telebot.TeleBot('7250191356:AAGpGt2-Fhs6sNfixhIucO0D7sU6lcqh7SI')

GOOGLE_SCRIPT_ID = 'https://script.google.com/macros/s/AKfycbzfJ0S9YFnclNy_ajuiw12sycebjGyqjvp_LlgOi251hbOAqKeBQL4J2YsskzLflLYqXg/exec'

message_ids = {}

# Храним данные пользователя
user_data = {}

last_messages = {}

# Вопросы на разных языках
questions = {
    'kazakh': {
        'start': "👋 Сәлем! 😊 Мен Айлинмін, Chicken Republic компаниясының онлайн рекрутерамын. Бізбен сұхбаттасып, бірнеше минут ішінде компаниямыздың артықшылықтары мен жұмыс шарттарымен танысыңыз. Сауалнаманы толтыруға небәрі 5 минут қана уақыт кетеді! 🕒",
        'phone': "📞 Телефон нөміріңізді енгізіңіз.\nМысалы: +7 777 123 45 67",
        'name': "📝 Толық аты-жөніңізді енгізіңіз:",
        'position': "💼 Қандай лауазымды таңдадыңыз?",
        'dob': "🎂 Туған күніңізді енгізіңіз (Күні.Айы.Жылы):",
        'bank': "🏦 Банк есепшотыңызда арест бар ма?",
        'schedule': "📅 Жұмыс шарттары туралы ақпарат",
        'address': "🏠 Қай мекен-жай сізге қолайлы?",
        'size': "👕 Киім өлшеміңіз қандай?",
        'experience': "🗂️ Жұмыс тәжірибеңіз туралы ",
        'thanks': "🎉 Рахмет! 🌟 Жақын арада біздің команда сізбен хабарласады. 🚀",
        'fail': "🚫 Өкінішке орай, біз тек 18 жастан асқандарды жұмысқа қабылдай аламыз. Мен сіздің деректеріңізді базамызға сақтап қоямын және жасыңыз сәйкес келген кезде сізбен хабарласамын. Сау болыңыз!",
        'failBank': "🚫 Міндетті түрде ресми тіркеу және төлемдер тек қызметкердің өз картасына ғана аударылады, сондықтан біз сізді жұмысқа ала алмаймыз. Мен сіздің түйіндемеңізді біздің деректер базасында сақтап, болашақта байланысқа шығамын, мүмкін сол уақытта шоттарыңыз бұғатталмаған болады. Сау болыңыз!",
        'failSalary': "🚫 Қазіргі уақытта бізде тек осындай жұмыс кестесі мен жалақы мөлшері қарастырылған, сондықтан сізді деректер базамызға сақтап қояйын, және басқа кесте немесе жалақы бойынша бос орындар пайда болғанда, сізбен хабарласамын. Сау болыңыз!"
    },
    'russian': {
        'start': "👋 Привет! 😊 Меня зовут Айлин, я онлайн рекрутер компании Chicken Republic. Приглашаю тебя пройти небольшое интервью и узнать больше о нашей компании и условиях работы. Это займет всего 5 минут! 🕒",
        'phone': "📞 Введите контактный номер телефона.\nНапример: +7 777 123 45 67",
        'name': "📝 Введите ваше ФИО:",
        'position': "💼 Какую должность вы выбираете?",
        'dob': "🎂 Введите дату рождения (День.Месяц.Год):",
        'bank': "🏦 Есть ли аресты на ваших банковских счетах?",
        'schedule': "📅 Информация о условиях работы",
        'address': "🏠 Какой адрес точки вам подходит?",
        'size': "👕 Какой у вас размер одежды?",
        'experience': "🗂️ Напишите свой размер:",
        'thanks': "🎉 Спасибо! 🌟 В ближайшее время с вами свяжется наша команда. 🚀",
        'fail': "🚫 К сожалению, мы можем принимать на работу только с 18 лет. Я сохраню ваши данные в нашей базе и свяжусь с вами, когда возраст позволит. Всего доброго!",
        'failBank': "🚫 У нас официальное оформление и выплаты только на карту самого сотрудника, поэтому не сможем взять вас на работу. Давайте я сохраню ваше резюме в нашей базе и свяжусь в будущем, возможно к этому времени ваши счета не будут заблокированы. Всего доброго!",
        'failSalary': "🚫 На данный момент у нас возможен только такой график и уровень зарплаты, поэтому давайте я сохраню вас в нашей базе и свяжусь с вами, когда появятся вакансии с другим графиком или оплатой. До свидания!"
    }
}

# Функция для проверки количества использований пользователя
def check_usage(chat_id):
    payload = {'chat_id': str(chat_id), 'action': 'check'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(GOOGLE_SCRIPT_ID, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'blocked' and 'blocked' or data.get('usage_count', 0)
    except requests.exceptions.RequestException:
        return 0

# Функция для обновления количества использований пользователя
def update_usage(chat_id):
    payload = {'chat_id': str(chat_id), 'action': 'update'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(GOOGLE_SCRIPT_ID, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('usage_count', 0)
    except requests.exceptions.RequestException:
        return 0


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # chat_id = '1321982385'
    message_id = message.message_id

    # Проверка количества использований пользователя
    usage_count = check_usage(chat_id)

    # if usage_count == '1321982385':
    #     print("Код продолжается")
    #     return

    if usage_count == 'blocked':
        # Если пользователь заблокирован, выводим сообщение и не продолжаем выполнение
        bot.send_message(chat_id, "⚠️ Вы превысили лимит использования бота. Пожалуйста, обратитесь за поддержкой для дальнейшей помощи. 🛠️\n⚠️ Сіз ботты пайдалану лимитінен асып кеттіңіз. Қосымша көмек алу үшін қолдау қызметіне хабарласыңыз. 🛠️")
        return  # Прекращаем выполнение

    if usage_count >= 3:
        bot.send_message(chat_id, "Вы превысили лимит использования бота. Обратитесь за поддержкой.")
        return  # Прекращаем выполнение, если лимит превышен

    

    # Обновляем количество запусков пользователя ОДИН РАЗ
    update_usage(chat_id)

    # Сохраняем ID для удаления позже
    if chat_id not in message_ids:
        message_ids[chat_id] = []

    # Создаем инлайн-кнопки для выбора языка
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Қазақша', callback_data='language_kazakh')
    btn2 = types.InlineKeyboardButton('Русский', callback_data='language_russian')
    markup.add(btn1, btn2)

    # Отправляем сообщение и сохраняем его ID для удаления
    msg = bot.send_message(
        chat_id,
        "<b>👋 Сәлем!</b>\n"
        "Мен <b>Chicken Republic</b> компаниясының онлайн-рекрутері боламын. 🕵️‍♂️\n"
        "Сізбен шағын сауалнама өткізейік, бұл 5 минуттан аспайды. ⏱️\n"
        "Сауалнамадан кейін біз компаниямыз және жұмыс шарттары туралы айтып береміз. 🏢📋\n\n"
        "<b>👋 Привет!</b>\n"
        "Я онлайн рекрутер компании <b>Chicken Republic</b>. 🕵️‍♂️\n"
        "Давай пройдем опрос, это займет не более 5 минут. ⏱️\n"
        "После опроса мы расскажем о нашей компании и условиях работы. 🏢📋\n\n"
        "<b>Тілді таңдаңыз:</b> / <b>Выберите язык</b>",
        reply_markup=markup,
        parse_mode='HTML'
    )

    try:
        bot.delete_message(chat_id, message_id)
    except telebot.apihelper.ApiException as e:
        print(f"Ошибка при удалении сообщения: {e}")

    # Сохраняем ID сообщения для удаления после выбора языка
    message_ids[chat_id].append(msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('language_'))
def handle_language_selection(call):
    chat_id = call.message.chat.id
    language = 'kazakh' if call.data == 'language_kazakh' else 'russian'
    user_data[chat_id] = {'language': language}

    if chat_id in message_ids:
        for msg_id in message_ids[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение {msg_id}: {e}")
        message_ids[chat_id] = []

    ask_phone(call.message)

def safe_delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Не удалось удалить сообщение {message_id}: {e}")

# Спрашиваем номер телефона и удаляем предыдущее сообщение
def ask_phone(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    msg = bot.send_message(chat_id, questions[language]['phone'])
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    chat_id = message.chat.id
    phone_number = message.text.replace(' ', '')
    bot_id = message.id - 1
    language = user_data[chat_id]['language']

    pattern = r"^(8|\+7)\d{10}$"

    if re.match(pattern, phone_number):
        user_data[chat_id]['phone'] = phone_number
        safe_delete_message(message.chat.id, message.id)
        safe_delete_message(message.chat.id, bot_id)
        ask_name(message)
    else:
        error_message = {
            'kazakh': "📞 Телефон нөміріңізді енгізіңіз.\nМысалы: +7 777 123 45 67",
            'russian': "📞 Введите контактный номер. \nНапример: +7 777 123 45 67"
        }
        msg = bot.send_message(chat_id, error_message[language])
        safe_delete_message(message.chat.id, message.id)
        safe_delete_message(message.chat.id, bot_id)
        bot.register_next_step_handler(msg, process_phone)




def process_custom_size(message):
    chat_id = message.chat.id
    user_size = message.text.strip()  # Получаем введенный пользователем размер

    # Проверяем, что размер не пустой
    if not user_size:
        msg = bot.send_message(chat_id, "Пожалуйста, введите корректный размер.")
        bot.register_next_step_handler(msg, process_custom_size)
        return

    # Сохраняем введенный размер
    user_data[chat_id]['size'] = user_size

    # Получаем язык пользователя
    language = user_data[chat_id].get('language', 'russian')

    # Отправляем сообщение с благодарностью
    bot.send_message(chat_id, questions[language]['thanks'])

    # Сохраняем данные в Google Sheets
    save_to_google_sheets(user_data[chat_id])

def ask_name(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    msg = bot.send_message(chat_id, questions[language]['name'])
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    chat_id = message.chat.id
    name = message.text.strip()
    bot_id = message.id - 1
    language = user_data[chat_id]['language']

    if len(name.split()) < 2:
        msg = bot.send_message(chat_id, questions[language]['name'])
        safe_delete_message(message.chat.id, message.id)
        safe_delete_message(message.chat.id, bot_id)
        bot.register_next_step_handler(msg, process_name)
    else:
        user_data[chat_id]['name'] = name
        safe_delete_message(message.chat.id, message.id)
        safe_delete_message(message.chat.id, bot_id)
        ask_position(message)

def ask_position(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🍴 Повар' if language == 'russian' else '🍴 Аспаз', callback_data='position_cook')
    btn2 = types.InlineKeyboardButton('📋 Менеджер' if language == 'russian' else '📋 Менеджер', callback_data='position_manager')
    btn3 = types.InlineKeyboardButton('💵 Кассир' if language == 'russian' else '💵 Кассир', callback_data='position_cashier')
    btn4 = types.InlineKeyboardButton('📦 Пакер' if language == 'russian' else '📦 Ораушы', callback_data='position_packager')
    markup.add(btn1, btn2, btn3, btn4)

    # Сохраняем сообщение с кнопками, чтобы потом его удалить
    msg = bot.send_message(chat_id, questions[language]['position'], reply_markup=markup)
    # Сохраняем ID сообщения
    user_data[chat_id]['position_message_id'] = msg.message_id


@bot.callback_query_handler(func=lambda call: call.data.startswith('position_'))
def handle_position_selection(call):
    chat_id = call.message.chat.id
    user_data[chat_id]['position'] = call.data.split('_')[1]

    # Удаление сообщения с инлайн-кнопками
    try:
        bot.delete_message(chat_id, user_data[chat_id]['position_message_id'])
    except Exception as e:
        print(f"Ошибка при удалении сообщения с кнопками: {e}")

    # Переход к следующему шагу
    ask_dob(call.message)


def ask_dob(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    msg = bot.send_message(chat_id, questions[language]['dob'])
    bot.register_next_step_handler(msg, process_dob)

def process_dob(message):
    chat_id = message.chat.id
    bot_id = message.id - 1
    language = user_data[chat_id]['language']  # Получаем язык пользователя

    try:
        user_data[chat_id]['dob'] = message.text
        age = calculate_age(user_data[chat_id]['dob'])
        user_data[chat_id]['age'] = age  # Сохраняем возраст пользователя в данные
        if age < 18:
            # Если возраст меньше 18, отправляем сообщение о невозможности принять на работу
            bot.send_message(chat_id, questions[language]['fail'])
            bot.delete_message(message.chat.id, message.id)
            bot.delete_message(message.chat.id, bot_id)
            save_to_google_sheets(user_data[chat_id], failed=True)  # Сохраняем данные
        else:
            # Если возраст больше 18, продолжаем дальше
            bot.delete_message(message.chat.id, message.id)
            bot.delete_message(message.chat.id, bot_id)
            ask_bank_status(message)  # Переход к следующему шагу
    except ValueError:
        # Сообщение об ошибке формата даты с переводом и смайликами
        error_message = "🎂 Введите дату рождения\nНапример: 25.12.2024" if language == 'russian' else "🎂 Туған күніңізді енгізіңіз. \nМысалы: 25.12.2024."
        msg = bot.send_message(chat_id, error_message)
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, bot_id)
        bot.register_next_step_handler(msg, process_dob)  # Повторяем шаг

def ask_bank_status(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да' if language == 'russian' else 'Иә', callback_data='bank_no')
    btn2 = types.InlineKeyboardButton('Нет' if language == 'russian' else 'Жоқ', callback_data='bank_no')
    markup.add(btn1, btn2)

    # Сохраняем сообщение с кнопками, чтобы потом его удалить
    msg = bot.send_message(chat_id, questions[language]['bank'], reply_markup=markup)

    # Сохраняем ID сообщения с кнопками
    user_data[chat_id]['bank_message_id'] = msg.message_id

@bot.callback_query_handler(func=lambda call: call.data == 'bank_yes' or call.data == 'bank_no')
def handle_bank_selection(call):
    chat_id = call.message.chat.id
    language = user_data[chat_id]['language']

    # Удаляем сообщение с кнопками "Да" или "Нет"
    try:
        bot.delete_message(chat_id, user_data[chat_id]['bank_message_id'])
    except Exception as e:
        print(f"Ошибка при удалении сообщения с кнопками: {e}")

    # Обработка выбора пользователя
    if call.data == 'bank_yes':
        user_data[chat_id]['bank'] = 'yes'  # Сохраняем значение 'yes' для арестованных счетов
        bot.send_message(chat_id, questions[language]['failBank'])
        # Сохраняем данные в Google Sheets и отмечаем, что кандидат не прошел отбор
        save_to_google_sheets(user_data[chat_id], failed=True)
    else:
        user_data[chat_id]['bank'] = 'no'  # Сохраняем значение 'no' для чистых счетов
        ask_schedule(call.message)  # Переход к следующему шагу

def ask_schedule(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    show_schedule_and_salary(message)

def show_schedule_and_salary(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    position = user_data[chat_id].get('position')

    if not position:
        bot.send_message(chat_id, "Ошибка: не выбрана должность. Пожалуйста, начните заново.")
        return

    # Словарь для хранения ID отправленных сообщений для дальнейшего удаления
    if chat_id not in message_ids:
        message_ids[chat_id] = []

    if language == 'russian':
        msg_info_header = bot.send_message(chat_id, "📅 Информация о условиях работы")
    elif language == 'kazakh':
        msg_info_header = bot.send_message(chat_id, "📅 Жұмыс шарттары туралы ақпарат")
    message_ids[chat_id].append(msg_info_header.message_id)  # Сохраняем ID

    # Данные о графике работы и зарплате для каждой должности
    schedules = {
        'cook': {
            'kazakh': "📅 <b>Жұмыс кестесі:</b>\n\n1️⃣ <b>Күндізгі бөлім студенттері үшін</b> таңертеңгі және кешкі ауысымда <b>8 сағаттық</b> икемді жұмыс кестесі\n2️⃣ <b>Сырттай бөлім студенттері мен басқа қызметкерлер үшін</b> <b>толық жұмыс күні</b>\n\n💰 <b>Жалақы:</b>\n\n💵 <b>Құзыреттерді бағалау тапсырылғанға дейін</b> — <b>500 тг/сағат</b>\n🔝 <b>Құзыреттерді бағалау тапсырылғаннан кейін</b> — <b>700 тг/сағат</b>\n🔄 <b>Егер құзыреттерді бағалауды сәтті тапсырсаңыз</b> — емтиханға дейінгі күндер есептеледі <b>700 тг/сағат</b>\n⚠️ <b>Егер құзыреттерді бағалауды сәтсіз тапсырсаңыз</b> — емтиханға дейін және кейінгі күндер есептеледі <b>500 тг/сағат</b>\n🔄 <b>Жалақы алдында қайта тапсыру мүмкіндігі бар</b>\n🎯 <b>Бонустар:</b>\n- Күнделікті жоспарды орындағаны үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>150 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>250 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>350 мың тг</b> үшін <b>+2000 тг</b>✨ <b>Шарттар:</b>\n- <b>2000 тг</b> 10 сағаттық ауысым үшін\n- 10 сағаттан аз болса — <b>1000 тг</b>\n\n💼 <b>Ең жоғары жалақы аспазшыға</b> — <b>250 000 тг</b>\n📊 <b>Орта есеппен біздің аспазшылар алады</b> — <b>160 000 тг</b>\n📝 <b>Ұсыныстар мен жақсартулар жүйесі:</b>\n- <b>500 тг</b> әр ұсыныс үшін\n- <b>100 $</b> әр айдың үздік ұсынысы үшін\n\n📚 Егер сізде жұмыс тәжірибесі болмаса, сіз <b>оқыту курсын</b> <b>5 күн</b> өтесіз, бірінші күннен бастап табыс таба аласыз және біздің командаға қосыласыз.\n\n🚍 <b>Жеткізу:</b> түнгі уақытта <b>23:00</b>-ден кейін қала ішінде (Рысқұлов - Әл-Фараби және Достық - Момышұлы бағыттары бойынша).\n\n🍽️ <b>Тамақтану:</b>\n- <b>2 рет тамақтану</b> <b>10 сағат және одан көп жұмыс істейтін</b> қызметкерлер үшін\n- <b>1 рет тамақтану</b> <b>10 сағаттан аз жұмыс істейтін</b> қызметкерлер үшін\n\n👕 <b>Форма:</b>\nБарлық қызметкерлерге <b>стажерлік форма</b> беріледі, ал еңбек шартына қол қойылғаннан кейін — білікті қызметкердің Chicken Republic формасы (бас киім, футболка және бейджик енгізілген).",


            'russian': "📅 <b>График работы:</b>\n\n1️⃣ <b>Гибкий график</b> работы для студентов очного вида обучения (8 часов, утренняя и вечерняя смены)\n2️⃣ <b>Полный рабочий день</b> для студентов заочного вида обучения и других сотрудников.\n\n💼 <b>Зарплата по вашей должности:</b>\n\n💵 <b>До сдачи оценки навыков</b> — <b>500 тг/час</b>\n🔝 <b>После сдачи оценки навыков</b> — <b>700 тг/час</b>\n🔄 <b>Если удачно сдаете оценку навыков</b> — дни до экзамена будут засчитаны по <b>700 тг/час</b>\n⚠️ <b>Если не удачно сдаете оценку навыков</b> — дни до и после экзамена будут засчитаны по <b>500 тг/час</b>\n🔄 <b>Есть возможность пересдачи перед зарплатой</b>\n🎯 <b>Бонусы:</b>\n <b>+2000 тг</b> за выполнение ежедневного плана продаж\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>150 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>250 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>350 тыс. тг</b>\n✨ <b>Условия:</b>\n- <b>2000 тг</b> за смену от 10 часов\n- Менее 10 часов — <b>1000 тг</b>\n\n💼 <b>Самая большая зарплата повара</b> — <b>250 000 тг</b>\n📊 <b>В среднем наши повара получают</b> — <b>160 000 тг</b>\n📝 <b>Система предложений и улучшений:</b>\n- <b>500 тг</b> за каждое предложение\n- <b>100 $</b> за лучшее предложение каждого месяца\n\n📚 Если у вас нет опыта работы, вы пройдёте <b>обучающий курс</b> <b>5 дней</b>, сможете начать зарабатывать с первого дня и стать частью нашей команды.\n\n🚍 <b>Развозка:</b> в ночное время после <b>23:00</b> в пределах города (Рыскулова-Аль-Фараби и Достык-Момушылы).\n\n🍽️ <b>Питание:</b>\n- <b>2-разовое питание</b> для сотрудников, работающих <b>10 часов и более</b>\n- <b>1-разовое питание</b> для сотрудников, работающих <b>менее 10 часов</b>\n\n👕 <b>Униформа:</b>\nВыдается <b>стажерская униформа</b> для всех сотрудников, после подписания трудового договора — форма квалифицированного сотрудника Chicken Republic (включает головной убор, футболку и бейджик)."

        },

        'manager': {
            'kazakh': "📅 <b>Жұмыс кестесі:</b>\n\n1️⃣ <b>Күндізгі бөлім студенттері үшін</b> таңертеңгі және кешкі ауысымда <b>8 сағаттық</b> икемді жұмыс кестесі\n2️⃣ <b>Сырттай бөлім студенттері мен басқа қызметкерлер үшін</b> <b>толық жұмыс күні</b>\n\n💰 <b>Жалақы:</b>\n\n💵 <b>Құзыреттерді бағалау тапсырылғанға дейін</b> — <b>700 тг/сағат</b>\n🔝 <b>Құзыреттерді бағалау тапсырылғаннан кейін</b> — <b>1000 тг/сағат</b>\n🔄 <b>Егер құзыреттерді бағалауды сәтті тапсырсаңыз</b> — емтиханға дейінгі күндер есептеледі <b>1000 тг/сағат</b>\n⚠️ <b>Егер құзыреттерді бағалауды сәтсіз тапсырсаңыз</b> — емтиханға дейін және кейінгі күндер есептеледі <b>700 тг/сағат</b>\n🔄 <b>Жалақы алдында қайта тапсыру мүмкіндігі бар</b>\n🎯 <b>Бонустар:</b>\n- Күнделікті жоспарды орындағаны үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>150 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>250 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>350 мың тг</b> үшін <b>+2000 тг</b>\n✨ <b>Шарттар:</b>\n- <b>2000 тг</b> 10 сағаттық ауысым үшін\n- 10 сағаттан аз болса — <b>1000 тг</b>\n\n💼 <b>Ең жоғары жалақы менеджерге</b> — <b>350 000 тг</b>\n📊 <b>Орта есеппен біздің менеджерлер алады</b> — <b>250 000 тг</b>\n📝 <b>Ұсыныстар мен жақсартулар жүйесі:</b>\n- <b>500 тг</b> әр ұсыныс үшін\n- <b>100 $</b> әр айдың үздік ұсынысы үшін\n\n📚 Егер сізде жұмыс тәжірибесі болмаса, сіз <b>оқыту курсын</b> <b>7 күн</b> өтесіз, бірінші күннен бастап табыс таба аласыз және біздің командаға қосыласыз.\n\n🚍 <b>Жеткізу:</b> түнгі уақытта <b>23:00</b>-ден кейін қала ішінде (Рысқұлов - Әл-Фараби және Достық - Момышұлы бағыттары бойынша).\n\n🍽️ <b>Тамақтану:</b>\n- <b>2 рет тамақтану</b> <b>10 сағат және одан көп жұмыс істейтін</b> қызметкерлер үшін\n- <b>1 рет тамақтану</b> <b>10 сағаттан аз жұмыс істейтін</b> қызметкерлер үшін\n\n👕 <b>Форма:</b>\nБарлық қызметкерлерге <b>стажерлік форма</b> беріледі, ал еңбек шартына қол қойылғаннан кейін — білікті қызметкердің Chicken Republic формасы (бас киім, футболка және бейджик енгізілген).",

            'russian': "📅 <b>График работы:</b>\n\n1️⃣ <b>Гибкий график</b> работы для студентов очного вида обучения (8 часов, утренняя и вечерняя смены)\n2️⃣ <b>Полный рабочий день</b> для студентов заочного вида обучения и других сотрудников.\n\n💼 <b>Зарплата по вашей должности:</b>\n\n💵 <b>До сдачи оценки навыков</b> — <b>700 тг/час</b>\n🔝 <b>После сдачи оценки навыков</b> — <b>1000 тг/час</b>\n🔄 <b>Если удачно сдаете оценку навыков</b> — дни до экзамена будут засчитаны по <b>1000 тг/час</b>\n⚠️ <b>Если не удачно сдаете оценку навыков</b> — дни до и после экзамена будут засчитаны по <b>700 тг/час</b>\n🔄 <b>Есть возможность пересдачи перед зарплатой</b>\n🎯 <b>Бонусы:</b>\n <b>+2000 тг</b> за выполнение ежедневного плана продаж\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>150 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>250 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>350 тыс. тг</b>\n✨ <b>Условия:</b>\n- <b>2000 тг</b> за смену от 10 часов\n- Менее 10 часов — <b>1000 тг</b>\n\n💼 <b>Самая большая зарплата менеджера</b> — <b>350 000 тг</b>\n📊 <b>В среднем наши менеджеры получают</b> — <b>250 000 тг</b>\n📝 <b>Система предложений и улучшений:</b>\n- <b>500 тг</b> за каждое предложение\n- <b>100 $</b> за лучшее предложение каждого месяца\n\n📚 Если у вас нет опыта работы, вы пройдёте <b>обучающий курс</b> <b>7 дней</b>, сможете начать зарабатывать с первого дня и стать частью нашей команды.\n\n🚍 <b>Развозка:</b> в ночное время после <b>23:00</b> в пределах города (Рыскулова-Аль-Фараби и Достык-Момушылы).\n\n🍽️ <b>Питание:</b>\n- <b>2-разовое питание</b> для сотрудников, работающих <b>10 часов и более</b>\n- <b>1-разовое питание</b> для сотрудников, работающих <b>менее 10 часов</b>\n\n👕 <b>Униформа:</b>\nВыдается <b>стажерская униформа</b> для всех сотрудников, после подписания трудового договора — форма квалифицированного сотрудника Chicken Republic (включает головной убор, футболку и бейджик)."

        },
        'cashier': {
            'kazakh': "📅 <b>График:</b>\n\n1️⃣ <b>Күндізгі бөлім студенттері үшін</b> таңғы және кешкі ауысымда <b>8 сағаттық</b> икемді жұмыс кестесі\n2️⃣ <b>Сырттай бөлім студенттері мен басқа қызметкерлер үшін</b> <b>толық жұмыс күні</b>\n\n💰 <b>Жалақы:</b>\n\n💵 <b>Құзыреттерді бағалау тапсырылғанға дейін</b> — <b>500 тг/сағат</b>\n🔝 <b>Құзыреттерді бағалау тапсырылғаннан кейін</b> — <b>700 тг/сағат</b>\n🔄 <b>Егер құзыреттерді бағалауды сәтті тапсырсаңыз</b> — емтиханға дейінгі күндер есептеледі <b>700 тг/сағат</b>\n⚠️ <b>Егер құзыреттерді бағалауды сәтсіз тапсырсаңыз</b> — емтиханға дейін және кейінгі күндер есептеледі <b>500 тг/сағат</b>\n🔄 <b>Жалақы алдында қайта тапсыру мүмкіндігі бар</b>\n🎯 <b>Бонустар:</b>\n- Күнделікті жоспарды орындағаны үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>150 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>250 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>350 мың тг</b> үшін <b>+2000 тг</b>\n✨ <b>Шарттар:</b>\n- <b>2000 тг</b> 10 сағаттық ауысым үшін\n- 10 сағаттан аз болса — <b>1000 тг</b>\n\n💼 <b>Ең жоғары жалақы кассирге</b> — <b>250 000 тг</b>\n📊 <b>Орта есеппен біздің кассирлер алады</b> — <b>160 000 тг</b>\n📝 <b>Ұсыныстар мен жақсартулар жүйесі:</b>\n- <b>500 тг</b> әр ұсыныс үшін\n- <b>100 $</b> әр айдың үздік ұсынысы үшін\n\n📚 Егер сізде жұмыс тәжірибесі болмаса, сіз <b>оқыту курсын</b> <b>7 күн</b> өтесіз, бірінші күннен бастап табыс таба бастай аласыз және біздің командаға қосыла аласыз.\n\n🚍 <b>Жеткізу:</b> түнгі уақытта <b>23:00</b> кейін қала ішінде (Рысқұлов - Әл-Фараби және Достық - Момышұлы бағыттары бойынша).\n\n🍽️ <b>Тамақтану:</b>\n- <b>2 рет тамақтану</b> <b>10 сағат және одан көп жұмыс істейтін</b> қызметкерлер үшін\n- <b>1 рет тамақтану</b> <b>10 сағаттан аз жұмыс істейтін</b> қызметкерлер үшін\n\n👕 <b>Форма:</b>\nБарлық қызметкерлерге <b>стажерлік форма</b> беріледі, ал еңбек шартына қол қойылғаннан кейін — білікті қызметкердің Chicken Republic формасы (бас киім, футболка және бейджик енгізілген).",

            'russian': "📅 <b>График работы:</b>\n\n1️⃣ <b>Гибкий график</b> работы для студентов очного вида обучения (8 часов, утренняя и вечерняя смены)\n2️⃣ <b>Полный рабочий день</b> для студентов заочного вида обучения и других сотрудников.\n\n💼 <b>Зарплата по вашей должности:</b>\n\n💵 <b>До сдачи оценки навыков</b> — <b>500 тг/час</b>\n🔝 <b>После сдачи оценки навыков</b> — <b>700 тг/час</b>\n🔄 <b>Если удачно сдаете оценку навыков</b> — дни до экзамена будут засчитаны по <b>700 тг/час</b>\n⚠️ <b>Если не удачно сдаете оценку навыков</b> — дни до и после экзамена будут засчитаны по <b>500 тг/час</b>\n🔄 <b>Есть возможность пересдачи перед зарплатой</b>\n🎯 <b>Бонусы:</b>\n <b>+2000 тг</b> за выполнение ежедневного плана продаж\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>150 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>250 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>350 тыс. тг</b>\n✨ <b>Условия:</b>\n- <b>2000 тг</b> за смену от 10 часов\n- Менее 10 часов — <b>1000 тг</b>\n\n💼 <b>Самая большая зарплата кассира</b> — <b>250 000 тг</b>\n📊 <b>В среднем наши кассиры получают</b> — <b>160 000 тг</b>\n📝 <b>Система предложений и улучшений:</b>\n- <b>500 тг</b> за каждое предложение\n- <b>100 $</b> за лучшее предложение каждого месяца\n\n📚 Если у вас нет опыта работы, вы пройдёте <b>обучающий курс</b> <b>7 дней</b>, сможете начать зарабатывать с первого дня и стать частью нашей команды.\n\n🚍 <b>Развозка:</b> в ночное время после <b>23:00</b> в пределах города (Рыскулова-Аль-Фараби и Достык-Момушылы).\n\n🍽️ <b>Питание:</b>\n- <b>2-разовое питание</b> для сотрудников, работающих <b>10 часов и более</b>\n- <b>1-разовое питание</b> для сотрудников, работающих <b>менее 10 часов</b>\n\n👕 <b>Униформа:</b>\nВыдается <b>стажерская униформа</b> для всех сотрудников, после подписания трудового договора — форма квалифицированного сотрудника Chicken Republic (включает головной убор, футболку и бейджик)."

        },
        'packager': {
            'kazakh': "📅 <b>График:</b>\n\n1️⃣ <b>Күндізгі бөлім студенттері үшін</b> таңғы және кешкі ауысымда <b>8 сағаттық</b> икемді жұмыс кестесі\n2️⃣ <b>Сырттай бөлім студенттері мен басқа қызметкерлер үшін</b> <b>толық жұмыс күні</b>\n\n💰 <b>Жалақы:</b>\n\n💵 <b>Құзыреттерді бағалау тапсырылғанға дейін</b> — <b>500 тг/сағат</b>\n🔝 <b>Құзыреттерді бағалау тапсырылғаннан кейін</b> — <b>700 тг/сағат</b>\n🔄 <b>Егер құзыреттерді бағалауды сәтті тапсырсаңыз</b> — емтиханға дейінгі күндер есептеледі <b>700 тг/сағат</b>\n⚠️ <b>Егер құзыреттерді бағалауды сәтсіз тапсырсаңыз</b> — емтиханға дейін және кейінгі күндер есептеледі <b>500 тг/сағат</b>\n🔄 <b>Жалақы алдында қайта тапсыру мүмкіндігі бар</b>\n🎯 <b>Бонустар:</b>\n- Күнделікті жоспарды орындағаны үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>150 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>250 мың тг</b> үшін <b>+2000 тг</b>\n- Күнделікті жоспарды орындау + <b>350 мың тг</b> үшін <b>+2000 тг</b>\n✨ <b>Шарттар:</b>\n- <b>2000 тг</b> 10 сағаттық ауысым үшін\n- 10 сағаттан аз болса — <b>1000 тг</b>\n\n💼 <b>Ең жоғары жалақы пакерге</b> — <b>250 000 тг</b>\n📊 <b>Орта есеппен біздің пакерлер алады</b> — <b>160 000 тг</b>\n📝 <b>Ұсыныстар мен жақсартулар жүйесі:</b>\n- <b>500 тг</b> әр ұсыныс үшін\n- <b>100 $</b> әр айдың үздік ұсынысы үшін\n\n📚 Егер сізде жұмыс тәжірибесі болмаса, сіз <b>оқыту курсын</b> <b>4 күн</b> өтесіз, бірінші күннен бастап табыс таба бастай аласыз және біздің командаға қосыла аласыз.\n\n🚍 <b>Жеткізу:</b> түнгі уақытта <b>23:00</b> кейін қала ішінде (Рысқұлов - Әл-Фараби және Достық - Момышұлы бағыттары бойынша).\n\n🍽️ <b>Тамақтану:</b>\n- <b>2 рет тамақтану</b> <b>10 сағат және одан көп жұмыс істейтін</b> қызметкерлер үшін\n- <b>1 рет тамақтану</b> <b>10 сағаттан аз жұмыс істейтін</b> қызметкерлер үшін\n\n👕 <b>Форма:</b>\nБарлық қызметкерлерге <b>стажерлік форма</b> беріледі, ал еңбек шартына қол қойылғаннан кейін — білікті қызметкердің Chicken Republic формасы (бас киім, футболка және бейджик енгізілген).",

            'russian': "📅 <b>График работы:</b>\n\n1️⃣ <b>Гибкий график</b> работы для студентов очного вида обучения (8 часов, утренняя и вечерняя смены)\n2️⃣ <b>Полный рабочий день</b> для студентов заочного вида обучения и других сотрудников.\n\n💼 <b>Зарплата по вашей должности:</b>\n\n💵 <b>До сдачи оценки навыков</b> — <b>500 тг/час</b>\n🔝 <b>После сдачи оценки навыков</b> — <b>700 тг/час</b>\n🔄 <b>Если удачно сдаете оценку навыков</b> — дни до экзамена будут засчитаны по <b>700 тг/час</b>\n⚠️ <b>Если не удачно сдаете оценку навыков</b> — дни до и после экзамена будут засчитаны по <b>500 тг/час</b>\n🔄 <b>Есть возможность пересдачи перед зарплатой</b>\n🎯 <b>Бонусы:</b>\n <b>+2000 тг</b> за выполнение ежедневного плана продаж\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>150 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>250 тыс. тг</b>\n <b>+2000 тг</b> за выполнение ежедневного плана + <b>350 тыс. тг</b>\n✨ <b>Условия:</b>\n- <b>2000 тг</b> за смену от 10 часов\n- Менее 10 часов — <b>1000 тг</b>\n\n💼 <b>Самая большая зарплата пакера</b> — <b>250 000 тг</b>\n📊 <b>В среднем наши пакеры получают</b> — <b>160 000 тг</b>\n📝 <b>Система предложений и улучшений:</b>\n- <b>500 тг</b> за каждое предложение\n- <b>100 $</b> за лучшее предложение каждого месяца\n\n📚 Если у вас нет опыта работы, вы пройдёте <b>обучающий курс</b> <b>4 дня</b>, сможете начать зарабатывать с первого дня и стать частью нашей команды.\n\n🚍 <b>Развозка:</b> в ночное время после <b>23:00</b> в пределах города (Рыскулова-Аль-Фараби и Достык-Момушылы).\n\n🍽️ <b>Питание:</b>\n- <b>2-разовое питание</b> для сотрудников, работающих <b>10 часов и более</b>\n- <b>1-разовое питание</b> для сотрудников, работающих <b>менее 10 часов</b>\n\n👕 <b>Униформа:</b>\nВыдается <b>стажерская униформа</b> для всех сотрудников, после подписания трудового договора — форма квалифицированного сотрудника Chicken Republic (включает головной убор, футболку и бейджик)."

        }
    }

    if position in schedules:
        # Отправляем информацию о графике и сохраняем ID сообщения
        msg_info = bot.send_message(chat_id, schedules[position][language], parse_mode='HTML')
        message_ids[chat_id].append(msg_info.message_id)

        # Создаем инлайн-кнопки для выбора
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('✅ Подходит' if language == 'russian' else '✅ Ұнайды', callback_data='accepted_schedule')
        btn2 = types.InlineKeyboardButton('❌ Не подходит' if language == 'russian' else '❌ Ұнамайды', callback_data='failed_schedule')
        markup.add(btn1, btn2)

        # Отправляем сообщение с выбором и сохраняем его ID
        msg_question = bot.send_message(chat_id, "Вас устраивает данный график и зарплата?" if language == 'russian' else "Сізге бұл жұмыс кестесі мен жалақы ұнай ма?", reply_markup=markup)

        # Проверяем, что bot.send_message возвращает объект сообщения, и сохраняем его ID
        if isinstance(msg_question, types.Message):
            message_ids[chat_id].append(msg_question.message_id)
        else:
            print("Ошибка: не удалось получить message_id.")


@bot.callback_query_handler(func=lambda call: call.data == 'accepted_schedule' or call.data == 'failed_schedule')
def handle_schedule_response(call):
    chat_id = call.message.chat.id
    language = user_data[chat_id]['language']

    # Удаляем все сохраненные сообщения (график работы, зарплата и выбор)
    if chat_id in message_ids:
        for msg_id in message_ids[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение {msg_id}: {e}")
        message_ids[chat_id] = []

    # Обрабатываем ответ
    if call.data == 'accepted_schedule':
        ask_address(call.message)  # Переход к следующему шагу
    else:
        bot.send_message(chat_id, questions[language]['failSalary'])
        save_to_google_sheets(user_data[chat_id], failed=True)

def ask_address(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Панфилова 111', callback_data='address_panfilova')
    btn2 = types.InlineKeyboardButton('Ритц Палас', callback_data='address_ritz')
    btn3 = types.InlineKeyboardButton('Орбита', callback_data='address_orbita')
    btn4 = types.InlineKeyboardButton('Форум', callback_data='address_forum')
    btn5 = types.InlineKeyboardButton('Атакент', callback_data='address_atakent')
    if language == 'russian':
        btn6 = types.InlineKeyboardButton('Все точки далеко', callback_data='address_all')
    elif language == 'kazakh':
        btn6 = types.InlineKeyboardButton('Барлық нүктелер алыс', callback_data='address_all')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    # Сохраняем сообщение с кнопками, чтобы потом его удалить
    msg = bot.send_message(chat_id, questions[language]['address'], reply_markup=markup)

    # Сохраняем ID сообщения с кнопками
    user_data[chat_id]['address_message_id'] = msg.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith('address_'))
def handle_address_selection(call):
    chat_id = call.message.chat.id
    user_data[chat_id]['address'] = call.data.split('_')[1]

    # Удаляем сообщение с кнопками адреса
    try:
        bot.delete_message(chat_id, user_data[chat_id]['address_message_id'])
    except Exception as e:
        print(f"Ошибка при удалении сообщения с кнопками: {e}")

    ask_size(call.message)  # Переход к следующему шагу


def ask_size(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('S', callback_data='size_s')
    btn2 = types.InlineKeyboardButton('M', callback_data='size_m')
    btn3 = types.InlineKeyboardButton('L', callback_data='size_l')
    btn4 = types.InlineKeyboardButton('XL', callback_data='size_xl')
    btn5 = types.InlineKeyboardButton('XXL', callback_data='size_xxl')
    if language == 'russian':
        btn6 = types.InlineKeyboardButton('Свой размер', callback_data='custom_size')
    elif language == 'kazakh':
        btn6 = types.InlineKeyboardButton('Өз өлшеміңіз', callback_data='custom_size')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    # Сохраняем сообщение с кнопками, чтобы потом его удалить
    msg = bot.send_message(chat_id, questions[language]['size'], reply_markup=markup)

    # Сохраняем ID сообщения с кнопками
    user_data[chat_id]['size_message_id'] = msg.message_id


@bot.callback_query_handler(func=lambda call: call.data.startswith('size_') or call.data == 'custom_size')
def handle_size_selection(call):
    chat_id = call.message.chat.id
    language = user_data[chat_id]['language']

    # Удаление сообщения с инлайн-кнопками
    try:
        bot.delete_message(chat_id, user_data[chat_id]['size_message_id'])
    except Exception as e:
        print(f"Ошибка при удалении сообщения с кнопками: {e}")

    # Проверка, если пользователь выбрал "Свой размер"
    if call.data == 'custom_size':
        if language == 'russian':
            msg = bot.send_message(chat_id, "Введите свой размер:")
        elif language == 'kazakh':
            msg = bot.send_message(chat_id, "Өз өлшеміңізді енгізіңіз:")
        bot.register_next_step_handler(msg, process_custom_size)  # Отправляем на обработку пользовательского размера
    else:
        # Сохраняем стандартный размер
        user_data[chat_id]['size'] = call.data.split('_')[1]
        check_age_and_size(call.message)  # Проверка возраста и размера

def check_age_and_size(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    age = user_data[chat_id].get('age', 0)
    size = user_data[chat_id].get('size', '')

    # Проверяем, если возраст >= 35 или пользователь выбрал "свой размер"
    if age >= 35 or size == 'custom':
        # Отправляем сообщение об отказе в работе
        if language == 'russian':
            msg = bot.send_message(chat_id,
                "Спасибо за ответы. На данный момент мы не готовы пригласить вас на работу к нам.\n\n"
                "Значит ваша работа мечты просто в другом месте - желаем её найти 🤝🏻."
            )
        elif language == 'kazakh':
            msg = bot.send_message(chat_id,
                "Жауаптарыңыз үшін рахмет. Қазіргі уақытта, өкінішке орай, біз сізді жұмысқа шақыруға дайын емеспіз.\n\n"
                "Біз сіздің арманыңыздағы жұмысыңыз басқа жерде екеніне сенімдіміз және оны табуыңызға сәттілік тілейміз 🤝🏻."
            )
        # Сохраняем данные в Google Sheets с пометкой "не прошли"
        save_to_google_sheets(user_data[chat_id], failed=True)
    else:
        # Если условия выполнены, продолжаем процесс
        finish_process(message)

def process_custom_size(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    user_size = message.text.strip()
    bot_id = message.id - 1

    if not user_size:
        # Если пользователь не ввел размер, просим его повторить
        if language == 'russian':
            msg = bot.send_message(chat_id, "Пожалуйста, введите корректный размер.")
        elif language == 'kazakh':
            msg = bot.send_message(chat_id, "Өлшемді дұрыс енгізіңіз.")
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, bot_id)
        bot.register_next_step_handler(msg, process_custom_size)
    else:
        # Сохраняем размер и отмечаем как "custom"
        user_data[chat_id]['size'] = 'custom'
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, bot_id)
        check_age_and_size(message)  # Проверка возраста и размера

def finish_process(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']

    # Благодарим пользователя и сохраняем данные
    msg = bot.send_message(chat_id, questions[language]['thanks'])

    # Проверяем, существует ли запись для chat_id в last_messages
    if chat_id not in last_messages:
        last_messages[chat_id] = {}  # Создаем пустую запись для chat_id

    # Сохраняем ID ответа в last_messages
    last_messages[chat_id]['answer'] = msg.message_id

    # Сохраняем данные в Google Sheets (или другую функцию)
    save_to_google_sheets(user_data[chat_id])



@bot.callback_query_handler(func=lambda call: call.data == 'accepted' or call.data == 'failedSalary')
def handle_response(call):
    chat_id = call.message.chat.id

    # Удаляем все сохраненные сообщения
    if chat_id in message_ids:
        for msg_id in message_ids[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение {msg_id}: {e}")

        # Очищаем список сообщений после удаления
        message_ids[chat_id] = []

    # Обрабатываем ответ пользователя
    if call.data == 'accepted':
        bot.send_message(chat_id, "Спасибо за ваш выбор! 🎉")
    elif call.data == 'failedSalary':
        bot.send_message(chat_id, "Жаль, что вам не подходит. Мы свяжемся с вами, когда появятся другие вакансии.")

def save_to_google_sheets(user_data, failed=False):
    data = {
        'phone': user_data.get('phone', ''),
        'name': user_data.get('name', ''),
        'position': user_data.get('position', ''),
        'dob': user_data.get('dob', ''),
        'age': user_data.get('age', 0),
        'bank': user_data.get('bank', 'no'),  # По умолчанию 'no', если не выбрано
        'address': user_data.get('address', 'unknown'),  # Если адрес не выбран, установить 'unknown'
        'size': user_data.get('size', 'unknown'),  # Если размер не выбран, установить 'unknown'
        'failed': 'true' if failed else 'false'
    }

    print("Отправляемые данные: ", data)

    headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }

    script_url = "https://script.google.com/macros/s/AKfycbyaDL0jsUYTQ4UHHJZws_erLFkqosLvz3Y0yhTfKSnPkrlR7nTy-DcCiA8WxRRw6Ed4/exec"

    try:
        response = requests.post(script_url, headers=headers, json=data)
        print(f"Статус ответа: {response.status_code}, Ответ: {response.text}")
    except Exception as e:
        print(f"Произошла ошибка при отправке данных: {e}")

def save_to_google_sheetsID(chat_id):
    # Подготовка данных для отправки
    data = {
        'chat_id': chat_id
    }

    # Адрес вашего скрипта Google Apps Script
    script_url = "https://script.google.com/macros/s/AKfycbzs6vKGNYT7OOKipDhMyyq_mfqBjkqTBp5CG-VpShk_ka5d7o_BUfAFIsK23_EWxvbSYA/exec"
    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }

    try:
        # Отправка запроса на сохранение данных в Google Sheets
        response = requests.post(script_url, headers=headers, json=data)
        print(f"Статус ответа: {response.status_code}, Ответ: {response.text}")
    except Exception as e:
        print(f"Произошла ошибка при отправке данных: {e}")

# Вычисление возраста
def calculate_age(dob):
    dob = datetime.strptime(dob, "%d.%m.%Y")
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            time.sleep(5)  

if __name__ == '__main__':
    run_bot()
