#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import unittest
import json
import os
import logging

# Non STL imports
import telegram
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Updater, Filters

from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot
from ptbtest import UserGenerator


# Local imports
from dcubabot import start, estasvivo, help, listar, listaroptativa, listarotro, messageLog
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
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.all, messageLog), group=1)
        dispatcher.add_handler(CommandHandler("help", help))
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("estasvivo", estasvivo))
        dispatcher.add_handler(CommandHandler("listar", listar))
        dispatcher.add_handler(CommandHandler("listaroptativa", listaroptativa))
        dispatcher.add_handler(CommandHandler("listarotro", listarotro))
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
        return user, chat

    def assert_command_sends_message(self, command, message_text):
        sent_messages_before = len(self.bot.sent_messages)
        self.sendCommand(command)
        self.assertEqual(len(self.bot.sent_messages) - sent_messages_before, 1)
        sent = self.bot.sent_messages[-1]
        self.assertEqual(sent['method'], "sendMessage")
        self.assertEqual(sent['text'], message_text)

    def test_help(self):
        with db_session:
            Command(name="comandoSinDescripcion1")
            Command(name="comandoConDescripcion1", description="Descripción 1")
            Command(name="comandoSinDescripcion2")
            Command(name="comandoConDescripcion2", description="Descripción 2")
            Command(name="comandoSinDescripcion3")
            Command(name="comandoConDescripcion3", description="Descripción 3")

        self.assert_command_sends_message("/help", ("/comandoConDescripcion1 - Descripción 1\n"
                                                    "/comandoConDescripcion2 - Descripción 2\n"
                                                    "/comandoConDescripcion3 - Descripción 3\n"))

    def test_start(self):
        self.assert_command_sends_message(
            "/start", "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")

    def test_estasvivo(self):
        self.assert_command_sends_message("/estasvivo", "Sí, estoy vivo.")

    # TODO: Rename
    def list_test(self, command, listable_type):
        self.assert_command_sends_message(command, "Grupos: ")

        # Assertions on keyboard
        inline_keyboard = json.loads(self.bot.sent_messages[-1]['reply_markup'])['inline_keyboard']
        self.assertEqual(len(inline_keyboard), 2)  # Number of rows
        for i in range(2):
            row = inline_keyboard[i]
            self.assertEqual((len(row)), 3)  # Number of columns
            for j in range(3):
                button = row[j]
                button_number = str(i * 3 + j)
                self.assertEqual(
                    button['text'], listable_type._discriminator_ + " " + button_number)
                self.assertEqual(button['url'], "https://url" + button_number + ".com")
                self.assertEqual(button['callback_data'], button['url'])

    def test_listar(self):
        self.list_test("/listar", Obligatoria)

    def test_listar(self):
        self.list_test("/listaroptativa", Optativa)

    def test_listar(self):
        self.list_test("/listarotro", Otro)

    def test_logger(self):
        with self.assertLogs("Bots.log", level='INFO') as cm:
            user, _ = self.sendCommand("/listar")
            first_message = 'INFO:Bots.log:'+str(user.id) + ': /listar'
            user, _ = self.sendCommand("/estasvivo")
            second_message = 'INFO:Bots.log:'+str(user.id)+': /estasvivo'
            self.assertEqual(cm.output, [first_message, second_message])


if __name__ == '__main__':
    unittest.main()
