#!/usr/bin/python3
# -*- coding: utf-8 -*-

# STL imports
import unittest
import json
import os
import logging
import datetime
# Non STL imports
import telegram
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Updater, Filters

from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot
from ptbtest import UserGenerator


# Local imports
from dcubabot import (start, estasvivo, help, listar, listaroptativa,
                      listarotro, cubawiki, log_message, felizdia_text,
                      rozendioanalisis, noitip, asm)
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
        init_db("test.sqlite3")
        with db_session:
            for listable_type in Listable.__subclasses__():
                for i in range(6):
                    listable_type(name=listable_type._discriminator_ + " " + str(i),
                                  url="https://url" + str(i) + ".com",
                                  validated=True)
        self.updater.start_polling()

    @classmethod
    def tearDownClass(self):
        self.updater.stop()
        os.remove("test.sqlite3")

    @classmethod
    def sendCommand(self, command, chat_id=None):
        user = self.ug.get_user(first_name="Test", last_name="The Bot")
        if chat_id:
            chat = self.cg.get_chat(chat_id)
        else:
            chat = self.cg.get_chat(user=user)
        update = self.mg.get_message(user=user, chat=chat, text=command)
        self.bot.insertUpdate(update)
        return user, chat

    def assert_bot_response(self, message_text, response_text, chat_id=None):
        sent_messages_before = len(self.bot.sent_messages)
        self.sendCommand(message_text, chat_id=chat_id)
        response_sent_messages = len(self.bot.sent_messages) - sent_messages_before
        if response_text:
            self.assertEqual(response_sent_messages, 1)
            sent = self.bot.sent_messages[-1]
            self.assertEqual(sent['method'], "sendMessage")
            if isinstance(response_text, str):
                self.assertEqual(sent['text'], response_text)
            else:
                self.assertIn(sent['text'], response_text)
        else:
            self.assertEqual(response_sent_messages, 0)

    def test_help(self):
        self.updater.dispatcher.add_handler(CommandHandler("help", help))
        with db_session:
            Command(name="comandoSinDescripcion1")
            Command(name="comandoConDescripcion1", description="Descripción 1")
            Command(name="comandoSinDescripcion2")
            Command(name="comandoConDescripcion2", description="Descripción 2")
            Command(name="comandoSinDescripcion3")
            Command(name="comandoConDescripcion3", description="Descripción 3")

        self.assert_bot_response("/help", ("/comandoConDescripcion1 - Descripción 1\n"
                                           "/comandoConDescripcion2 - Descripción 2\n"
                                           "/comandoConDescripcion3 - Descripción 3\n"))

    def test_start(self):
        self.updater.dispatcher.add_handler(CommandHandler("start", start))
        self.assert_bot_response(
            "/start", "Hola, ¿qué tal? ¡Mandame /help si no sabés qué puedo hacer!")

    def test_estasvivo(self):
        self.updater.dispatcher.add_handler(CommandHandler("estasvivo", estasvivo))
        self.assert_bot_response("/estasvivo", "Sí, estoy vivo.")

    def test_rozendioanalisis(self):
        self.updater.dispatcher.add_handler(CommandHandler("rozendioanalisis", rozendioanalisis))
        self.assert_bot_response("/rozendioanalisis", "No. Rozen todavia no dio el final de análisis.")

    # TODO: Rename
    def list_test(self, command, listable_type):
        self.assert_bot_response(command, "Grupos: ")

        # Assertions on keyboard
        inline_keyboard = json.loads(self.bot.sent_messages[-1]['reply_markup'])['inline_keyboard']
        self.assertEqual(len(inline_keyboard), 2)  # Number of rows
        for i in range(2):
            row = inline_keyboard[i]
            self.assertEqual((len(row)), 3)  # Number of columns
            for j in range(3):
                button = row[j]
                button_number = i * 3 + j
                self.assertEqual(
                    button['text'], listable_type._discriminator_ + " " + str(button_number))
                self.assertEqual(button['url'], "https://url" + str(button_number) + ".com")
                self.assertEqual(button['callback_data'], button['url'])

    def test_listar(self):
        self.updater.dispatcher.add_handler(CommandHandler("listar", listar))
        self.list_test("/listar", Obligatoria)

    def test_listaroptativa(self):
        self.updater.dispatcher.add_handler(CommandHandler("listaroptativa", listaroptativa))
        self.list_test("/listaroptativa", Optativa)

    def test_listarotro(self):
        self.updater.dispatcher.add_handler(CommandHandler("listarotro", listarotro))
        self.list_test("/listarotro", Otro)

    def test_logger(self):
        self.updater.dispatcher.add_handler(MessageHandler(Filters.all, log_message), group=1)
        with self.assertLogs("DCUBABOT", level='INFO') as cm:
            user, _ = self.sendCommand("/listar")
            first_message = 'INFO:DCUBABOT:'+str(user.id) + ': /listar'
            user, _ = self.sendCommand("/estasvivo")
            second_message = 'INFO:DCUBABOT:'+str(user.id)+': /estasvivo'
            self.assertEqual(cm.output, [first_message, second_message])

    def test_cubawiki(self):
        self.updater.dispatcher.add_handler(CommandHandler("cubawiki", cubawiki))
        cubawiki_url = "https://www.cubawiki.com.ar/index.php/Segundo_Parcial_del_10/12/18"
        positive_chat_id = -123456
        negative_chat_id_no_cubawiki = -654321
        negative_chat_id_no_entry = -123321
        with db_session:
            Obligatoria(name="Cubawiki", url="test.com",
                        chat_id=positive_chat_id, cubawiki_url=cubawiki_url)
            Obligatoria(name="Cubawiki", url="test.com", chat_id=negative_chat_id_no_cubawiki)

        # Positive test case
        self.assert_bot_response("/cubawiki", cubawiki_url, chat_id=positive_chat_id)

        # Negative test cases
        self.assert_bot_response("/cubawiki", None, chat_id=negative_chat_id_no_cubawiki)
        self.assert_bot_response("/cubawiki", None, chat_id=negative_chat_id_no_entry)

        with db_session:
            delete(o for o in Obligatoria if o.name == "Cubawiki")

    def test_felizdia(self):
        today = datetime.datetime(2019, 1, 1)
        self.assertEqual(felizdia_text(today), "Feliz 1 de Enero")
        today = datetime.datetime(2019, 2, 1)
        self.assertEqual(felizdia_text(today), "Feliz 1 de Febrero")
        today = datetime.datetime(2019, 3, 1)
        self.assertEqual(felizdia_text(today), "Feliz 1 de Marzo")
        today = datetime.datetime(2019, 4, 4)
        self.assertEqual(felizdia_text(today), "Feliz 4 de Abril")
        today = datetime.datetime(2019, 5, 21)
        self.assertEqual(felizdia_text(today), "Feliz 21 de Mayo")

    # TODO: Test randomness?
    def test_noitip(self):
        self.updater.dispatcher.add_handler(CommandHandler("noitip", noitip))
        noitips = ["me siento boludeadisimo", "Not this shit again", "noitip"]
        with db_session:
            for phrase in noitips:
                Noitip(text=phrase)

        self.assert_bot_response("/noitip", noitips)

    def test_asm(self):
        self.updater.dispatcher.add_handler(CommandHandler("asm", asm, pass_args=True))
        with db_session:
            AsmInstruction(mnemonic="AAD",
                           summary="ASCII Adjust AX Before Division",
                           url="https://www.felixcloutier.com/x86/aad")
            AsmInstruction(mnemonic="ADD",
                           summary="Add",
                           url="https://www.felixcloutier.com/x86/add")
            AsmInstruction(mnemonic="ADDPD",
                           summary="Add Packed Double-Precision Floating-Point Values",
                           url="https://www.felixcloutier.com/x86/addpd")
            AsmInstruction(mnemonic="MOV",
                           summary="Move to/from Control Registers",
                           url="http://www.felixcloutier.com/x86/MOV-1.html")
            AsmInstruction(mnemonic="MOV",
                           summary="Move to/from Debug Registers",
                           url="http://www.felixcloutier.com/x86/MOV-2.html")
            AsmInstruction(mnemonic="INT n",
                           summary="Call to Interrupt Procedure",
                           url="http://www.felixcloutier.com/x86/INT%20n:INTO:INT%203.html")

        not_found = "No pude encontrar esa instrucción."
        possibles = not_found + "\nQuizás quisiste decir:"
        add_info = ("[ADD] Descripción: Add.\n"
                    "Más info: https://www.felixcloutier.com/x86/add")
        addpd_info = ("[ADDPD] Descripción: Add Packed Double-Precision Floating-Point Values.\n"
                      "Más info: https://www.felixcloutier.com/x86/addpd")
        mov1_info = ("[MOV] Descripción: Move to/from Control Registers.\n"
                     "Más info: http://www.felixcloutier.com/x86/MOV-1.html")
        mov2_info = ("[MOV] Descripción: Move to/from Debug Registers.\n"
                     "Más info: http://www.felixcloutier.com/x86/MOV-2.html")
        intn_info = ("[INT n] Descripción: Call to Interrupt Procedure.\n"
                     "Más info: http://www.felixcloutier.com/x86/INT%20n:INTO:INT%203.html")

        self.assert_bot_response("/asm", "No me pasaste ninguna instrucción.")
        self.assert_bot_response("/asm add", add_info)
        self.assert_bot_response("/asm ADDPD", addpd_info)
        self.assert_bot_response("/asm a", not_found)
        self.assert_bot_response("/asm Adp", possibles + "\n" + add_info)
        self.assert_bot_response("/asm ADDPS", possibles + "\n" + addpd_info)
        self.assert_bot_response("/asm addP", possibles + "\n" + add_info + "\n" + addpd_info)
        self.assert_bot_response("/asm MOV", mov1_info + "\n" + mov2_info)
        self.assert_bot_response("/asm INT n", intn_info)


if __name__ == '__main__':
    unittest.main()
