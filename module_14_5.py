from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import get_all_products, add_user, is_included
import sqlite3

ap_token = ""
bot = Bot(token=ap_token)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')  # Новая кнопка

kb.add(button, button2, button3, button4)

kb_inline = InlineKeyboardMarkup()
button_inline = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_inline2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inline.add(button_inline, button_inline2)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()  # Значение будет установлено по умолчанию (1000)


@dp.message_handler(text='Регистрация')
async def sing_up(message: types.Message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text.strip()

    if is_included(username):  # Проверка наличия пользователя в базе
        await message.answer("Пользователь существует, введите другое имя.")
        return

    await state.update_data(username=username)
    await message.answer("Введите свой email:")
    await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    age = await validate_numeric_input(message)
    if age is None:
        return

    await state.update_data(age=age)
    data = await state.get_data()

    # Установка баланса по умолчанию
    balance = 1000
    data['balance'] = balance

    # Добавление пользователя в базу
    add_user(data['username'], data['email'], data['age'])

    await message.answer("Регистрация прошла успешно")
    await state.finish()



def generate_product_keyboard():
    products = get_all_products()
    keyboard = InlineKeyboardMarkup(row_width=4)

    buttons = [
        InlineKeyboardButton(text=product[1], callback_data=f"product_{product[0]}")
        for product in products
    ]
    keyboard.add(*buttons)
    return keyboard


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


async def on_startup(dp):
    print("Загрузка данных из таблицы Products...")
    products = get_all_products()
    print("Продукты в базе данных:", products)


async def validate_numeric_input(message: types.Message):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return None
    value = int(message.text)
    return value


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью', reply_markup=kb)


@dp.message_handler(text='Информация')
async def info(message: types.Message):
    await message.answer('AvernBot, version 1.3')


@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


@dp.message_handler(text='Купить')
async def buy_menu(message: types.Message):
    await get_buying_list(message)


def get_product_images(product_id, db_name="products.db"):
    """Получает все изображения для продукта с заданным ID."""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT image_path FROM ProductImages WHERE product_id = ?", (product_id,))
    images = cursor.fetchall()

    connection.close()
    return [image[0] for image in images]


async def get_buying_list(message: types.Message):
    products = get_all_products()

    if not products:
        await message.answer("В базе данных нет продуктов.")
        return

    for product in products:
        product_id, title, description, price = product[:4]
        text = f"Название: {title} | Описание: {description} | Цена: {price}"
        await message.answer(text)

        # Получение изображений для текущего продукта
        image_paths = get_product_images(product_id)
        for image_path in image_paths:
            try:
                with open(image_path, 'rb') as photo:
                    await message.answer_photo(photo)
            except FileNotFoundError:
                await message.answer(f"Изображение {image_path} для продукта {title} не найдено.")

    await message.answer("Выберите продукт для покупки:", reply_markup=generate_product_keyboard())


@dp.callback_query_handler(lambda call: call.data.startswith('product_'))
async def send_confirm_message(call: types.CallbackQuery):
    product_id = call.data.split('_')[1]
    await call.message.answer(f'Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer('10 x вес(кг) + 6.25 x рост(см) - 5 x возраст(г) - 161')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    age = await validate_numeric_input(message)
    if age is None:
        return
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    growth = await validate_numeric_input(message)
    if growth is None:
        return
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    weight = await validate_numeric_input(message)
    if weight is None:
        return
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f'Ваша норма калорий: {calories:.2f}')
    await state.finish()


@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
