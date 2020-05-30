#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def error_callback(update, context):
    logger.exception(context.error)
