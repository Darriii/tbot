import unittest
from unittest.mock import patch, MagicMock
from telebot import TeleBot
import config

# Импорт функций из файла с кодом бота
from tbot import send_welcome, select_group, send_schedule, send_news, send_events, feedback_prompt, send_help

class TestTelegramBot(unittest.TestCase):

    def setUp(self):
        self.bot = TeleBot(config.token)
        self.user_id = config.ADMIN_ID
        self.username = "test_user"

    def create_message(self, text):
        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = self.user_id
        message.from_user = MagicMock()
        message.from_user.username = self.username
        message.text = text
        return message

    @patch('telebot.TeleBot.send_message')
    def test_start_command(self, mock_send_message):
        message = self.create_message('/start')
        send_welcome(message)
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertIn("Выбери свою группу", args[1])

    @patch('telebot.TeleBot.send_message')
    def test_select_group(self, mock_send_message):
        message = self.create_message('1-ТИД-5')
        select_group(message)
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertIn("Нажмите на кнопку, чтобы получить расписание", args[1])

    @patch('telebot.TeleBot.send_message')
    def test_get_schedule(self, mock_send_message):
        message = self.create_message('Расписание на сегодня')
        send_schedule(message)
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertIn("Сегодня", args[1])

    @patch('telebot.TeleBot.send_message')
    def test_get_news(self, mock_send_message):
        message = self.create_message('Новости')
        send_news(message)
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertTrue("Нет новостей" in args[1] or "Последние новости" in args[1])

    @patch('telebot.TeleBot.send_message')
    def test_get_events(self, mock_send_message):
        message = self.create_message('Мероприятия')
        send_events(message)
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertTrue("Нет мероприятий" in args[1] or "Последние мероприятия" in args[1])

    @patch('telebot.TeleBot.send_message')
    def test_feedback(self, mock_send_message):
        message = self.create_message('Обратная связь')
        feedback_prompt(message)
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertIn("Введите ваше сообщение для методиста", args[1])

    @patch('telebot.TeleBot.send_message')
    def test_help(self, mock_send_message):
        message = self.create_message('Помощь')
        send_help(message)
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertIn("Список доступных команд", args[1])

if __name__ == '__main__':
    unittest.main()
