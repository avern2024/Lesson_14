from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ap_token = ""
bot = Bot(token=ap_token)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.add(button, button2)

button3 = KeyboardButton(text='Купить')
kb.add(button3)

kb_inline = InlineKeyboardMarkup()
button_inline = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_inline2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inline.add(button_inline, button_inline2)

kb_inline2 = InlineKeyboardMarkup(row_width=4)
button_inline = InlineKeyboardButton(text='Клубника', callback_data='product_buying')
button_inline2 = InlineKeyboardButton(text='Томаты', callback_data='product_buying')
button_inline3 = InlineKeyboardButton(text='Мандарины', callback_data='product_buying')
button_inline4 = InlineKeyboardButton(text='Яблоки', callback_data='product_buying')
kb_inline2.add(button_inline, button_inline2, button_inline3, button_inline4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


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
    await message.answer('AvernBot, version 1.1')


@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


@dp.message_handler(text='Купить')
async def buy_menu(message: types.Message):
    await get_buying_list(message)


async def get_buying_list(message: types.Message):
    products = [
        {"name": "Клубника", "description": "41 ккал", "price": 500, "image": "kl.jpg"},
        {"name": "Томаты", "description": "20 ккал", "price": 200, "image": "tomat.jpg"},
        {"name": "Мандарины", "description": "38 ккал", "price": 252, "image": "mandarin.jpg"},
        {"name": "Яблоки", "description": "47 ккал", "price": 140, "image": "apple.jpg"},
    ]

    for product in products:
        text = (f'Название: {product["name"]} | Калорий в 100г: {product["description"]} | Цена руб за кг:'
                f' {product["price"]}')
        await message.answer(text)

        with open(product["image"], 'rb') as photo:
            await message.answer_photo(photo)

    await message.answer('Выберите продукт для покупки:', reply_markup=kb_inline2)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.answer('Вы успешно приобрели продукт!')


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
    executor.start_polling(dp, skip_updates=True)
