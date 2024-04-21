import asyncio
import logging
from re import L
import config
# import model
# from duble_video_model import Duplicate_video_model
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, Video
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.types.message import ContentType
from aiogram import F
import datetime
from datetime import datetime, timedelta
from time import sleep
from db import DataBase
from model import Duplicate_video_model
import os
from download_video import downloader_from_google_drive, downloader_from_YouTube


data_base = DataBase()

TOKEN = config.TOKEN  # "6724577554:AAEtTdPpz1l-CzbwwC7pbFPX97DTIROO_5E"

# prices
PRICE = types.LabeledPrice(label='monthly subscription', amount=500 * 100)  # в копейках

router = Router()
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode="HTML")
model = Duplicate_video_model()


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    chat_id = message.chat.id
    if not data_base.check_user_existence(user_id=chat_id):
        data_base.add_user(
            user_id=chat_id,
            count_free_translate=1,
            have_subscription=False,
            date_due=datetime.now()
        )
    builder.add(types.InlineKeyboardButton(
        text="Duplicate video",
        callback_data="video_duplicate")
    )
    builder.add(types.InlineKeyboardButton(
        text="Settings",
        callback_data="settings")
    )
    builder.add(types.InlineKeyboardButton(
        text="Developers",
        callback_data="developer")
    )
    builder.add(types.InlineKeyboardButton(
        text="Buy subscription",
        callback_data="buy_subscription")
    )

    image_from_pc = FSInputFile("picture.jpg")
    await message.answer_photo(
        image_from_pc,
        caption=f"Hello, <b>{message.from_user.full_name}</b>! I'm Automatic Video Duplication AI bot."
                f" You can send me a video and I will duplicate it on another language!"
                f" Try it, just click <b>Duplicate video</b> button!",
        reply_markup=builder.as_markup()
    )


@dp.message(Command("duplicate_video"))
async def duplicate_video(message: Message, command: CommandObject) -> None:
    url, type_disk = command.args.split()
    print(url, type_disk)
    language = data_base.get_language(user_id=message.chat.id)
    if language == None:
        await message.answer("You haven't selected a language! Do it in settings.")
    else:
        #file_id = message.video.file_id  # Get file id
        #file = await bot.get_file(file_id)  # Get file path

        if not os.path.exists(f'{message.chat.id}/'):
            os.makedirs(f'{message.chat.id}/')
            print('--------Folder was created')

        if os.path.exists(f"{message.chat.id}/video.mp4"):
            os.remove(f"{message.chat.id}/video.mp4")

        if type_disk.lower() == 'google_drive':
            downloader_from_google_drive(url, f"{message.chat.id}/video.mp4")
        elif type_disk.lower() == 'youtube':
            downloader_from_YouTube(url, f"{message.chat.id}", filename='video.mp4')
        #await bot.download_file(file.file_path,
        #                        f"{message.chat.id}/video.mp4")
        print('--------File was downloaded')
        print('--------File if predicting')
        model.predict(f"{message.chat.id}/video.mp4", language, f'{message.chat.id}/video_{message.chat.id}/',
                      f"{message.chat.id}/final.mp4", message.chat.id)
        print('--------File if predict')
        print('--------Video was created')

        while True:
            if os.path.exists(f"{message.chat.id}/final.mp4"):
                print('find file')
                break
            else:
                pass
        await bot.send_video(message.chat.id, FSInputFile(f"{message.chat.id}/final.mp4"))


@dp.callback_query(F.data == "video_duplicate")
async def duplicate_video(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='Back 🔙',
        callback_data='main'
    ))
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer('To take advantage of duplication, you must send a video and sign\n' +
                                  ' the comment /duplicate_video url type(google_drive or youtube) for it, then write the language into which \n' +
                                  'you want to translate, namely, select from the list.',
                                  reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'buy_subscription')
async def bay_subscription(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    print(chat_id)

    if data_base.get_have_subscription(user_id=chat_id):
        await bot.send_message(chat_id, 'You already have a subscription')
    else:
        print(callback.message)
        # if config.PAYMENST_TOKEN.split(':')[1] == 'TEST':
        #     await bot.send_message(chat_id, 'Test payment!!!')
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await bot.send_invoice(
            chat_id,
            title='subscription to video duplication',
            description='Activation of subscription for 1 month',
            provider_token=config.PAYMENST_TOKEN,
            currency='rub',
            # photo_url='https://upload.wikimedia.org/wikipedia/commons/c/ce/Noaa-walrus22.jpg',
            is_flexible=False,
            prices=[PRICE],
            start_parameter='one-month-subscription',
            payload='test-invoice-payload',
        )


@dp.callback_query(F.data == "main")
async def settings(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    message = callback.message
    chat_id = message.chat.id
    if not data_base.check_user_existence(user_id=chat_id):
        data_base.add_user(
            user_id=chat_id,
            count_free_translate=1,
            have_subscription=False,
            date_due=datetime.now()
        )
    builder.add(types.InlineKeyboardButton(
        text="Duplicate video",
        callback_data="video_duplicate")
    )
    builder.add(types.InlineKeyboardButton(
        text="Settings",
        callback_data="settings")
    )
    builder.add(types.InlineKeyboardButton(
        text="Developers",
        callback_data="developer")
    )
    builder.add(types.InlineKeyboardButton(
        text="Buy subscription",
        callback_data="buy_subscription")
    )

    image_from_pc = FSInputFile("picture.jpg")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await message.answer_photo(
        image_from_pc,
        caption=f"Hello, <b>{message.from_user.full_name}</b>! I'm Automatic Video Duplication AI bot."
                f" You can send me a video and I will duplicate it on another language!"
                f" Try it, just click <b>Duplicate video</b> button!",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "english")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("English is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "English")


@dp.callback_query(F.data == "spanish")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Spanish is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Spanish")


@dp.callback_query(F.data == "french")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("French is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "french")


@dp.callback_query(F.data == "german")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("German is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "German")


@dp.callback_query(F.data == "italian")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Italian is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Italian")


@dp.callback_query(F.data == "portuguese")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Portuguese is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Portuguese")


@dp.callback_query(F.data == "polish")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Polish is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Polish")


@dp.callback_query(F.data == "turkish")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Turkish is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Turkish")


@dp.callback_query(F.data == "Russian")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Russian is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Russian")


@dp.callback_query(F.data == "czech")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Czech is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Czech")


@dp.callback_query(F.data == "dutch")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Dutch is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Dutch")


@dp.callback_query(F.data == "arabic")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Arabic is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Arabic")


@dp.callback_query(F.data == "chinese")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Chinese is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Chinese")


@dp.callback_query(F.data == "japanese")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Japanese is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Japanese")


@dp.callback_query(F.data == "hungarian")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Hungarian is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Hungarian")


@dp.callback_query(F.data == "korean")
async def settings(callback: types.CallbackQuery):
    await callback.message.answer("Korean is selected language!")
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    data_base.update_language(callback.message.chat.id, "Korean")


# pre checkout
@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message(F.successful_payment)  # SUCCESSFUL_PAYMENT
async def successful_payment(message: types.Message):
    print('successful payment:')
    chat_id = message.chat.id
    print(message.successful_payment.model_json_schema())
    print(type(message.successful_payment.model_json_schema()))
    payment_info = message.successful_payment.model_json_schema()
    for k, v in payment_info.items():
        if type(v) == dict:
            for k_, v_ in v.items():
                print(f'{k_} = {v_}')
        else:
            print(f'{k} = {v}')
    data_base.update_date_due(user_id=chat_id, new_date_due=datetime.now())
    data_base.update_have_subscription(user_id=chat_id, new_subscription=True)
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Back 🔙',
            callback_data='main'
        )
    )
    await bot.send_message(chat_id,
                           f'Payment for the amount {message.successful_payment.total_amount // 100}'
                           f' {message.successful_payment.currency} was succesfull!', reply_markup=builder.as_markup())


@dp.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="English 🇺🇸",
            callback_data="english"),
        types.InlineKeyboardButton(
            text="Spanish 🇪🇸",
            callback_data="spanish"),
        types.InlineKeyboardButton(
            text="French 🇫🇷",
            callback_data="french"),
        types.InlineKeyboardButton(
            text="German 🇩🇪",
            callback_data="german"),
        width=4
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Italian 🇮🇹",
            callback_data="italian"),
        types.InlineKeyboardButton(
            text="Portuguese 🇵🇹",
            callback_data="portuguese"),
        types.InlineKeyboardButton(
            text="Polish 🇵🇱",
            callback_data="polish"),
        types.InlineKeyboardButton(
            text="Turkish 🇹🇷",
            callback_data="turkish"),
        width=4
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Russian 🇷🇺",
            callback_data="russian"),
        types.InlineKeyboardButton(
            text="Dutch 🇩🇰",
            callback_data="dutch"),
        types.InlineKeyboardButton(
            text="Czech 🇨🇿",
            callback_data="czech"),
        types.InlineKeyboardButton(
            text="Arabic 🇦🇪",
            callback_data="arabic"),
        width=4
    )

    builder.row(
        types.InlineKeyboardButton(
            text="Chinese 🇨🇳",
            callback_data="chinese"),
        types.InlineKeyboardButton(
            text="Japanese 🇯🇵",
            callback_data="japanese"),
        types.InlineKeyboardButton(
            text="Hungarian 🇭🇺",
            callback_data="hungarian"),
        types.InlineKeyboardButton(
            text="Korean 🇰🇷",
            callback_data="korean"),
        width=4
    )

    builder.row(
        types.InlineKeyboardButton(
            text='Back 🔙',
            callback_data='main'
        ),
        width=1
    )
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(
        f'You can change your language here. Now your language is {data_base.get_language(user_id=callback.message.chat.id)}. Just click any button!',
        reply_markup=builder.as_markup())


@dp.callback_query(F.data == "developer")
async def developer(callback: types.CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Back 🔙',
            callback_data='main'
        )
    )
    await callback.message.answer("This bot and AI was created by @artyomjk @EgorAndrik",
                                  reply_markup=builder.as_markup())


@dp.message(Command('data'))
async def see_data(message: types.Message):
    data_base.print_all_data()


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
