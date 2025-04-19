import logging
import sqlite3 # Убедитесь, что sqlite3 импортирован здесь
import os      # Импортируем os для работы с путями

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from decouple import config

# --- Начало: Конфигурация пути к БД для Railway Volume ---
VOLUME_MOUNT_PATH = '/data'  # Это путь, который вы указываете в Railway Volumes
DB_FILENAME = 'bot.db'       # Имя вашего файла БД
DB_PATH = os.path.join(VOLUME_MOUNT_PATH, DB_FILENAME) # Полный путь к файлу БД

# Убедимся, что директория для Volume существует (Railway ее создает, но лучше проверить)
# os.makedirs создаст директорию, если ее нет, и не выдаст ошибку, если она уже есть
os.makedirs(VOLUME_MOUNT_PATH, exist_ok=True)
logging.info(f"Используется путь к базе данных: {DB_PATH}")
# --- Конец: Конфигурация пути к БД ---


API_TOKEN = config('TOKEN')
logging.basicConfig(level=logging.INFO)

# Инициализация бота и MemoryStorage
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# database.py (содержимое теперь внутри main.py)

def create_tables():
    """Создание таблиц в базе данных с использованием пути из Volume"""
    conn = None
    try:
        # ---- ИЗМЕНЕНО ----
        # УДАЛЕНО: Проверка и удаление старой БД. Нам нужно сохранять данные!
        # if os.path.exists(DB_PATH):
        #     try:
        #         os.remove(DB_PATH) # НЕ УДАЛЯТЬ БД ПРИ КАЖДОМ ЗАПУСКЕ!
        #         logging.info("Старая база данных удалена.")
        #     except PermissionError:
        #         logging.error("Ошибка: Файл bot.db занят...")
        #         return

        # ---- ИЗМЕНЕНО ----
        # Используем DB_PATH для подключения
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Создаем таблицу users с уникальным chat_id
        # (IF NOT EXISTS предотвратит ошибку, если таблицы уже созданы)
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY,
                          first_name TEXT,
                          last_name TEXT,
                          username TEXT,
                          chat_id INTEGER UNIQUE)''')

        # Исправленная таблица test_results
        cursor.execute('''CREATE TABLE IF NOT EXISTS test_results (
                          first_name TEXT,
                          last_name TEXT,
                          username TEXT,
                          result TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (
                          user_id INTEGER UNIQUE)''') # Добавил UNIQUE, чтобы избежать дублей

        cursor.execute('''CREATE TABLE IF NOT EXISTS discounts (
                          id INTEGER PRIMARY KEY,
                          description TEXT,
                          start_date TEXT,
                          end_date TEXT)''')

        conn.commit()
        logging.info("Таблицы успешно созданы или уже существуют.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite при создании таблиц: {e}")
    finally:
        if conn:
            conn.close()

# ... (Остальные классы и переменные, как TestStates, catalog_data - БЕЗ ИЗМЕНЕНИЙ) ...
class TestStates(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()
    question5 = State()
    question6 = State()
    question7 = State()
    question8 = State()
    question9 = State()
    question10 = State()
    question11 = State()

catalog_data = {
    "Android": (
        "🔧 Хочешь создавать приложения, которые будут жить в карманах миллионов людей?\n\n"
        "Здесь ты научишься разрабатывать крутые мобильные приложения для Android — от первых строчек кода до публикации в Google Play.\n\n"
        "Стань тем, кто делает технологии ближе к людям!",
        "https://www.instagram.com/genesis.academy.kg/"
    ),
    "UX/UI": (
        "🎨 Погрузись в мир дизайна, где красота встречается с удобством!\n\n"
        "Ты будешь создавать интерфейсы, которые радуют глаз и делают жизнь проще. От скетчей до прототипов — твоё творчество изменит способ взаимодействия с цифровым миром!",
        "https://www.instagram.com/genesis.academy.kg/"
    ),
    "Frontend": (
        "🌐 Стань создателем веб-магии!\n\n"
        "Освой HTML, CSS и JavaScript, чтобы оживлять сайты и делать их удобными на любом устройстве. Каждый клик и каждая анимация — результат твоей работы, вдохновляющей пользователей!",
        "https://www.instagram.com/genesis.academy.kg/"
    ),
    "Backend": (
        "🛠 Загляни за кулисы интернета!\n\n"
        "Здесь ты научишься строить мощные серверы, которые поддерживают работу веб-приложений. Данные, логика, безопасность — стань невидимым героем, держащим всё на плаву!",
        "https://www.instagram.com/genesis.academy.kg/"
    ),
    "FullStack": (
        "💻 Хочешь уметь всё? Это твой путь!\n\n"
        "Освой как клиентскую (Frontend), так и серверную (Backend) часть, чтобы создавать полноценные приложения от А до Я. Будь универсальным мастером, готовым воплотить любую идею в жизнь!",
        "https://www.instagram.com/genesis.academy.kg/"
    )
}


# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user = message.from_user
    # ---- ИЗМЕНЕНО ----
    conn = sqlite3.connect(DB_PATH) # Используем DB_PATH
    cursor = conn.cursor()
    try:
        # Используем INSERT OR IGNORE чтобы не было ошибки при дубликате chat_id
        cursor.execute(
            "INSERT OR IGNORE INTO users (first_name, last_name, username, chat_id) VALUES (?, ?, ?, ?)",
            (user.first_name, user.last_name, user.username, message.chat.id)
        )
        conn.commit()
    except sqlite3.Error as e:
         logging.error(f"Ошибка SQLite в /start: {e}")
    finally:
        conn.close()

    await message.reply(
        "🌟 Привет! Добро пожаловать в мир крутых возможностей! 🌟 Я твой верный помощник, готовый помочь выбрать направление обучения, которое раскроет твой талант и приведёт к успеху!\n\n"
        "🚀 Вот что я могу для тебя:\n"
        "- Пройди увлекательный /test, чтобы понять, какое направление тебе ближе всего.\n"
        "- Загляни в наш /catalog — там множество интересных направлений, которые ждут тебя!\n"
        "- Хочешь быть в курсе всех новинок? Подпишись на /subscribe и получай новости о курсах, мероприятиях и скидках прямо в чат.\n"
        "- Если надоело получать новости, воспользуйся /unsubscribe.\n"
        "- Узнай о текущих /discounts и хватай лучшие предложения!"
    )

# --- Обработчики команды /test (q1 - q10) ---
# В этих обработчиках нет прямого взаимодействия с БД, поэтому они БЕЗ ИЗМЕНЕНИЙ
# (код для q1 - q10 опущен для краткости, он остается таким же)
@dp.message_handler(commands=['test'])
async def start_test(message: types.Message):
    await TestStates.question1.set()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Мне нравится, когда всё красиво и удобно 😊", callback_data="q1_a"),
        types.InlineKeyboardButton(text="b) Я люблю разбираться, как всё устроено внутри 🧐", callback_data="q1_b"),
        types.InlineKeyboardButton(text="c) Мне нравится, когда всё просто работает ⚙️", callback_data="q1_c"),
        types.InlineKeyboardButton(text="d) Мне интересно, как делают приложения на телефоне 📱", callback_data="q1_d")
    )
    await message.reply("Вопрос 1: Что тебе ближе? 🤔", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("q1_"), state=TestStates.question1)
async def process_q1(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q1'] = answer
    await TestStates.next()
    # ... остальной код для q1 -> q2 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Придумывать, как он будет выглядеть 🎨", callback_data="q2_a"),
        types.InlineKeyboardButton(text="b) Настраивать, чтобы всё работало правильно 🔧", callback_data="q2_b"),
        types.InlineKeyboardButton(text="c) Делать так, чтобы им было удобно пользоваться 🖥️", callback_data="q2_c"),
        types.InlineKeyboardButton(text="d) Делать приложение, которое можно установить на телефон 📲", callback_data="q2_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 2: Представь, что ты создаёшь продукт. Что ты хочешь делать? 🤩",
                           reply_markup=keyboard)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("q2_"), state=TestStates.question2)
async def process_q2(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q2'] = answer
    await TestStates.next()
    # ... остальной код для q2 -> q3 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Очень нравится! 😍", callback_data="q3_a"),
        types.InlineKeyboardButton(text="b) Иногда, по настроению 🤔", callback_data="q3_b"),
        types.InlineKeyboardButton(text="c) Не особо, мне больше нравится логика 🤓", callback_data="q3_c"),
        types.InlineKeyboardButton(text="d) Я больше люблю делать что-то полезное, чем красивое 👍", callback_data="q3_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 3: Насколько тебе нравится рисовать или оформлять что-то? 🎨",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q3_"), state=TestStates.question3)
async def process_q3(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q3'] = answer
    await TestStates.next()
    # ... остальной код для q3 -> q4 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Компьютер и сайты 🖥️", callback_data="q4_a"),
        types.InlineKeyboardButton(text="b) Телефон и приложения 📱", callback_data="q4_b"),
        types.InlineKeyboardButton(text="c) Всё, где можно что-то придумать и красиво оформить 🌟", callback_data="q4_c"),
        types.InlineKeyboardButton(text="d) Не важно — главное, чтобы работало быстро и чётко ⚡", callback_data="q4_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 4: Какие устройства тебе интереснее всего? 🤖",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q4_"), state=TestStates.question4)
async def process_q4(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q4'] = answer
    await TestStates.next()
    # ... остальной код для q4 -> q5 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Я визуал — люблю, когда всё красиво 🎨", callback_data="q5_a"),
        types.InlineKeyboardButton(text="b) Я люблю логику, порядок и правила 📐", callback_data="q5_b"),
        types.InlineKeyboardButton(text="c) Мне важно, чтобы людям было удобно 😊", callback_data="q5_c"),
        types.InlineKeyboardButton(text="d) Мне интересно, как создаются приложения на телефоне 📱", callback_data="q5_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 5: Как ты думаешь, что тебе ближе по духу? 💡",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q5_"), state=TestStates.question5)
async def process_q5(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q5'] = answer
    await TestStates.next()
    # ... остальной код для q5 -> q6 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Собирать картинки, вдохновляться дизайнами 🖼️", callback_data="q6_a"),
        types.InlineKeyboardButton(text="b) Решать головоломки и логические задачи 🧩", callback_data="q6_b"),
        types.InlineKeyboardButton(text="c) Думать, как сделать что-то понятным для других 🤔", callback_data="q6_c"),
        types.InlineKeyboardButton(text="d) Придумывать что-то новое для смартфона 📲", callback_data="q6_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 6: Что тебе больше нравится? 💭",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q6_"), state=TestStates.question6)
async def process_q6(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q6'] = answer
    await TestStates.next()
    # ... остальной код для q6 -> q7 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Учиться рисовать интерфейсы 🎨", callback_data="q7_a"),
        types.InlineKeyboardButton(text="b) Учиться писать код, чтобы всё работало 💻", callback_data="q7_b"),
        types.InlineKeyboardButton(text="c) Учиться делать удобные сайты 🌐", callback_data="q7_c"),
        types.InlineKeyboardButton(text="d) Учиться создавать мобильные приложения 📱", callback_data="q7_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 7: Если бы ты учился новому, что тебе ближе? 📚",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q7_"), state=TestStates.question7)
async def process_q7(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q7'] = answer
    await TestStates.next()
    # ... остальной код для q7 -> q8 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Работать с цветами, шрифтами и стилями 🌈", callback_data="q8_a"),
        types.InlineKeyboardButton(text="b) Настраивать, чтобы всё работало без ошибок 🔧", callback_data="q8_b"),
        types.InlineKeyboardButton(text="c) Создавать то, что видит и использует пользователь 👀", callback_data="q8_c"),
        types.InlineKeyboardButton(text="d) Делать то, что можно использовать на телефоне 📲", callback_data="q8_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 8: Представь, что ты работаешь в IT. Что тебе приятнее делать? 🤩",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q8_"), state=TestStates.question8)
async def process_q8(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q8'] = answer
    await TestStates.next()
    # ... остальной код для q8 -> q9 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Искусство, черчение 🎨", callback_data="q9_a"),
        types.InlineKeyboardButton(text="b) Математика, физика 🔢", callback_data="q9_b"),
        types.InlineKeyboardButton(text="c) Литература, обществознание 📚", callback_data="q9_c"),
        types.InlineKeyboardButton(text="d) Труд, информатика 💻", callback_data="q9_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 9: Какие предметы в школе тебе были ближе? 📖",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q9_"), state=TestStates.question9)
async def process_q9(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q9'] = answer
    await TestStates.next()
    # ... остальной код для q9 -> q10 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Через картинки и примеры 🖼️", callback_data="q10_a"),
        types.InlineKeyboardButton(text="b) Пошагово, с логикой 🔍", callback_data="q10_b"),
        types.InlineKeyboardButton(text="c) Простыми словами, чтобы было понятно 🗣️", callback_data="q10_c"),
        types.InlineKeyboardButton(text="d) Показываю прямо на телефоне 📱", callback_data="q10_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 10: Как ты обычно объясняешь что-то другим? 🧐",
                           reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("q10_"), state=TestStates.question10)
async def process_q10(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data.split("_")[1]
    async with state.proxy() as data:
        data['q10'] = answer
    await TestStates.next()
    # ... остальной код для q10 -> q11 ...
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="a) Делать красивые макеты для сайтов/приложений 🎨", callback_data="q11_a"),
        types.InlineKeyboardButton(text="b) Писать сложную логику и программы 🖥️", callback_data="q11_b"),
        types.InlineKeyboardButton(text="c) Делать сайты, которые работают на телефоне и ПК 🌐", callback_data="q11_c"),
        types.InlineKeyboardButton(text="d) Делать приложения для Android 🤖", callback_data="q11_d")
    )
    await bot.send_message(callback_query.from_user.id,
                           "Вопрос 11: Что из этого ты хотел бы уметь? 💪",
                           reply_markup=keyboard)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("q11_"), state=TestStates.question11)
async def process_q11(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка 11 вопроса и сохранение результата"""
    # ... (логика определения result - БЕЗ ИЗМЕНЕНИЙ) ...
    async with state.proxy() as data:
        # ---- ДОБАВЛЕНО: Получаем ответ на q11 ----
        answer = callback_query.data.split("_")[1]
        data['q11'] = answer
        # -----------------------------------------
        answers = [data.get(f'q{i}') for i in range(1, 12)] # Теперь до 12 включительно
        counts = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
        for ans in answers:
            if ans in counts:
                counts[ans] += 1

        # Если есть 'd', Android - приоритет
        if counts.get('d', 0) > 0:
             direction = 'd'
        # Иначе, если 'a' и 'c' равны и больше 'b', то Fullstack
        elif counts.get('a', 0) > 0 and counts.get('a', 0) == counts.get('c', 0) and counts.get('a', 0) > counts.get('b', 0):
            result = 'FullStack-разработка' # Отдельная логика для FullStack
        # Иначе выбираем максимум
        else:
             # Находим ключ с максимальным значением. Если есть несколько максимумов,
             # вернется один из них (порядок может быть не гарантирован)
             non_d_counts = {k: v for k, v in counts.items() if k != 'd'}
             if not non_d_counts: # Если только 'd' были или вообще нет ответов
                 direction = 'd' # Или можно выбрать другое дефолтное значение
             else:
                 direction = max(non_d_counts, key=non_d_counts.get)

        # Если результат не был 'FullStack', используем карту
        if 'result' not in locals(): # Проверяем, была ли уже присвоена переменная result
            direction_map = {
                'a': 'UX/UI-дизайн',
                'b': 'Backend-разработка',
                'c': 'Frontend-разработка',
                'd': 'Android-разработка'
            }
            result = direction_map.get(direction, 'Не определено')


        user = callback_query.from_user
        conn = None # Инициализируем conn
        try:
            # ---- ИЗМЕНЕНО ----
            conn = sqlite3.connect(DB_PATH) # Используем DB_PATH
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO test_results
                            (first_name, last_name, username, result)
                            VALUES (?, ?, ?, ?)''',
                          (user.first_name,
                           user.last_name,
                           user.username,
                           result))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Ошибка сохранения результата теста: {e}")
            await bot.send_message(callback_query.from_user.id, "❌ Произошла ошибка при сохранении вашего результата.") # Отправляем сообщение пользователю
            await state.finish() # Завершаем состояние в случае ошибки
            return # Выходим из функции
        finally:
            if conn:
                conn.close()

    await state.finish()
    await bot.send_message(
        callback_query.from_user.id,
        f"🎉 Ваш результат: *{result}*\n\n"
        "Похоже, это направление тебе подходит! 😉\n"
        "Хочешь узнать больше? Загляни в наш каталог!\n\n"
        "👉 /catalog",
        parse_mode="Markdown"
    )
    await callback_query.answer() # Отвечаем на callback query


# Команда /catalog — вывод каталога направлений (БЕЗ ИЗМЕНЕНИЙ)
@dp.message_handler(commands=['catalog'])
async def send_catalog(message: types.Message):
    result_text = "📚 *Каталог направлений:*\n\n"
    for direction, data in catalog_data.items():
        description, link = data
        result_text += (
            f"🔹 *{direction}*\n\n"
            f"{description}\n\n"
            f"👉 [Подробнее]({link})\n\n"
            f"{'-'*40}\n\n"
        )
    await message.reply(result_text, parse_mode="Markdown", disable_web_page_preview=True) # Добавил disable_web_page_preview

# Команда /subscribe
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    conn = None
    try:
        # ---- ИЗМЕНЕНО ----
        conn = sqlite3.connect(DB_PATH) # Используем DB_PATH
        cursor = conn.cursor()
        # Используем INSERT OR IGNORE для простоты и атомарности
        cursor.execute("INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)", (message.from_user.id,))
        # rowcount покажет, была ли вставлена новая строка (1) или запись уже существовала (0)
        if cursor.rowcount > 0:
            conn.commit()
            await message.reply("Вы успешно подписались на новости! 📢")
        else:
            await message.reply("Вы уже подписаны на новости 😊")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite в /subscribe: {e}")
        await message.reply("❌ Произошла ошибка при подписке.")
    finally:
        if conn:
            conn.close()


# Команда /unsubscribe
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    conn = None
    try:
        # ---- ИЗМЕНЕНО ----
        conn = sqlite3.connect(DB_PATH) # Используем DB_PATH
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscribers WHERE user_id = ?", (message.from_user.id,))
        conn.commit()
        # Проверяем, была ли строка удалена
        if cursor.rowcount > 0:
             await message.reply("Вы отписались от новостей. 👋")
        else:
             await message.reply("Вы и так не были подписаны. 🤔")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite в /unsubscribe: {e}")
        await message.reply("❌ Произошла ошибка при отписке.")
    finally:
        if conn:
            conn.close()


# Команда /discounts
@dp.message_handler(commands=['discounts'])
async def send_discounts(message: types.Message):
    conn = None
    try:
        # ---- ИЗМЕНЕНО ----
        conn = sqlite3.connect(DB_PATH) # Используем DB_PATH
        cursor = conn.cursor()
        # Убедитесь, что формат дат в БД совместим с date('now') SQLite (YYYY-MM-DD)
        cursor.execute("SELECT description FROM discounts WHERE end_date >= date('now') ORDER BY end_date") # >= чтобы включить текущий день
        discounts = cursor.fetchall()

        if discounts:
            discounts_text = "🔥 *Актуальные скидки и акции:*\n\n" + "\n\n".join([f"• {d[0]}" for d in discounts])
        else:
            discounts_text = "На данный момент активных скидок нет. Следите за обновлениями! 😉"
        await message.reply(discounts_text, parse_mode="Markdown")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite в /discounts: {e}")
        await message.reply("❌ Не удалось загрузить информацию о скидках.")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # Создаем таблицы ПЕРЕД запуском бота
    create_tables()
    # Запускаем бота
    executor.start_polling(dp, skip_updates=True)