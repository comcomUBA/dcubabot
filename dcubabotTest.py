#!/usr/bin/python3
# -*- coding: utf-8 -*-
import unittest

import telegram
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot
from ptbtest import UserGenerator

from dcubabot import start, estasvivo, help


class TestDCUBABot(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # For use within the tests we nee some stuff. Starting with a Mockbot
        self.bot = Mockbot()
        self.bot.request = telegram.utils.request.Request()
        # Some generators for users and chats
        self.ug = UserGenerator()
        self.cg = ChatGenerator()
        # And a Messagegenerator and updater (for use with the bot.)
        self.mg = MessageGenerator(self.bot)
        self.updater = Updater(bot=self.bot)
        self.updater.dispatcher.add_handler(CommandHandler("help", help))
        self.updater.dispatcher.add_handler(CommandHandler("start", start))
        self.updater.dispatcher.add_handler(CommandHandler("estasvivo", estasvivo))
        print("Hice setup")
        self.updater.start_polling()

    @classmethod
    def tearDownClass(self):
        self.updater.stop()

    def test_help(self):
        update = self.mg.get_message(text="/help")
        self.bot.insertUpdate(update)
        # self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], "Yo tampoco sé qué puedo hacer.")

    def test_start(self):
        user = self.ug.get_user(first_name="Test", last_name="The Bot")
        chat = self.cg.get_chat(user=user)
        update = self.mg.get_message(user=user, chat=chat, text="/start")
        self.bot.insertUpdate(update)
        # self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(
            sent['text'], "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")

    def test_estasvivo(self):
        user = self.ug.get_user(first_name="Test", last_name="The Bot")
        chat = self.cg.get_chat(user=user)
        update = self.mg.get_message(user=user, chat=chat, text="/estasvivo")
        self.bot.insertUpdate(update)
        # self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], "Sí, estoy vivo.")


if __name__ == '__main__':
    unittest.main()
