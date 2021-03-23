# !/usr/bin/python3
# -*- coding: utf-8 -*-

# https://stackoverflow.com/a/11236372/1576803
import datetime

import pytz


def get_hora_feliz_dia():
    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    now = datetime.datetime.now(tz).date()
    midnight = tz.localize(datetime.datetime.combine(now, datetime.time(0, 0, 3)), is_dst=None)
    return midnight.astimezone(pytz.utc).time()


def get_hora_update_groups():
    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    now = datetime.datetime.now(tz).date()
    midnight = tz.localize(datetime.datetime.combine(now, datetime.time(0, 1, 3)), is_dst=None)
    return midnight.astimezone(pytz.utc).time()
