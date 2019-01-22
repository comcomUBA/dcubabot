#!/usr/bin/python3
# -*- coding: utf-8 -*-


def error_callback(bot, update, error):
    logger.exception(error)
