# -*- coding: utf-8 -*-
import datetime
import random

from peewee import *

# db = MySQLDatabase(host = 'localhost', user = 'root', passwd = 'qwer1234', database = 'test', charset = 'utf8')
db = SqliteDatabase('people.db')


class FaceUser(Model):
    nickname = CharField(max_length=9)
    face_url = CharField()
    register_date = DateTimeField(default=datetime.datetime.now)
    last_time_date = DateTimeField(default=datetime.datetime.now)
    remember_token = CharField(max_length=20)

    @staticmethod
    def get_remember_token(num):
        return "".join([str(random.randrange(9)) for i in range(num)])

    class Meta:
        database = db


def create_new_user(name, face_url):
    r = FaceUser.get_remember_token(4)
    item = FaceUser(
        nickname=name,
        face_url=face_url,
        remember_token=r
    )
    item.save()
    return r


def find_user(code):
    return FaceUser.select().where(FaceUser.remember_token == code)
