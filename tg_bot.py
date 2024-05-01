import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import io

# Установка токена вашего бота
bot = telebot.TeleBot("")

def show_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Вывести спектрограмму композиции", callback_data='get_spectrogram')
    keyboard.add(button)
    bot.send_message(chat_id, 'Вот, что я умею:', reply_markup=keyboard)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    try:
        show_menu(message.chat.id)
    except Exception as e:
        handle_error(message.chat.id, e)

# Функция для отправки сообщения об ошибке
def handle_error(chat_id, error):
    bot.send_message(chat_id, f"Произошла ошибка: {error}. Пожалуйста, попробуйте ещё раз позже.")

# Обработчик нажатия кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == 'get_spectrogram':
            bot.send_message(call.message.chat.id, 'Для продолжения необходимо загрузить аудиофайл или отправить голосовое сообщение.')
    except Exception as e:
        handle_error(call.message.chat.id, e)

# Обработчик для загрузки аудиофайла
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        bot.send_message(message.chat.id, 'Рисую спектрограмму...')
        audio_data = io.BytesIO()
        if message.content_type == 'audio':
            file_id = message.audio.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            audio_data.write(downloaded_file)
            audio_data.seek(0)
        elif message.content_type == 'voice':
            file_id = message.voice.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            audio_data.write(downloaded_file)
            audio_data.seek(0)

        y, sr = librosa.load(audio_data)
        D = np.abs(librosa.stft(y))
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(librosa.amplitude_to_db(D, ref=np.max), sr=sr, x_axis='time', y_axis='log')
        plt.title('Спектрограмма аудиофайла')
        plt.colorbar(format='%+2.0f dB')
        plt.tight_layout()

        img_data = io.BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)

        bot.send_photo(message.chat.id, img_data)
        bot.send_message(message.chat.id, 'Выполнение задачи завершено, давайте я для Вас ещё что-нибудь сделаю?')
        show_menu(message.chat.id)  # Показываем меню после отправки спектрограммы
    except Exception as e:
        handle_error(message.chat.id, e)

# Запуск бота
bot.polling()
