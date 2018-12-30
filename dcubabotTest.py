#!/usr/bin/python3
# -*- coding: utf-8 -*-
import unittest

import json
import os

import telegram
from telegram.ext import CommandHandler
from telegram.ext import Updater

from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot
from ptbtest import UserGenerator

from dcubabot import start, estasvivo, help, listar, listaroptativa, listarotro
from models import *


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
        self.updater.dispatcher.add_handler(CommandHandler("listar", listar))
        self.updater.dispatcher.add_handler(CommandHandler("listaroptativa", listaroptativa))
        self.updater.dispatcher.add_handler(CommandHandler("listarotro", listarotro))
        init_db("test.sqlite3")
        with db_session:
            for listable_type in Listable.__subclasses__():
                for i in range(6):
                    listable_type(name=listable_type._discriminator_ + " " + str(i),
                                  url="https://url" + str(i) + ".com")
        print("Hice setup")
        self.updater.start_polling()

    @classmethod
    def tearDownClass(self):
        self.updater.stop()
        os.remove("test.sqlite3")

    @classmethod
    def sendCommand(self, command):
        user = self.ug.get_user(first_name="Test", last_name="The Bot")
        chat = self.cg.get_chat(user=user)
        update = self.mg.get_message(user=user, chat=chat, text=command)
        self.bot.insertUpdate(update)

    def test_help(self):
        with db_session:
            Command(name="comandoSinDescripcion1")
            Command(name="comandoConDescripcion1", description="Descripción 1")
            Command(name="comandoSinDescripcion2")
            Command(name="comandoConDescripcion2", description="Descripción 2")
            Command(name="comandoSinDescripcion3")
            Command(name="comandoConDescripcion3", description="Descripción 3")

        self.sendCommand("/help")
        # self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], ("/comandoConDescripcion1 - Descripción 1\n"
                                        "/comandoConDescripcion2 - Descripción 2\n"
                                        "/comandoConDescripcion3 - Descripción 3\n"))

    def test_start(self):
        self.sendCommand("/start")
        # self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(
            sent['text'], "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")

    def test_estasvivo(self):
        self.sendCommand("/estasvivo")
        # self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], "Sí, estoy vivo.")

    # TODO: Rename
    def list_test(self, command, listable_type):
        self.sendCommand(command)
        # self.assertEqual(len(self.bot.sent_messages), 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], "Grupos: ")

        # Assertions on keyboard
        inline_keyboard = json.loads(sent['reply_markup'])['inline_keyboard']
        self.assertEqual(len(inline_keyboard), 2)  # Number of rows
        for i in range(2):
            row = inline_keyboard[i]
            self.assertEqual((len(row)), 3)  # Number of columns
            for j in range(3):
                button = row[j]
                button_number = str(i * 3 + j)
                self.assertEqual(button['text'], listable_type._discriminator_ + " " + button_number)
                self.assertEqual(button['url'], "https://url" + button_number + ".com")
                self.assertEqual(button['callback_data'], button['url'])

    def test_listar(self):
        self.list_test("/listar", Obligatoria)

    def test_listar(self):
        self.list_test("/listaroptativa", Optativa)

    def test_listar(self):
        self.list_test("/listarotro", Otro)


if __name__ == '__main__':
    unittest.main()
