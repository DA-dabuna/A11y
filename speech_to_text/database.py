# -*- coding: utf-8 -*-
import datetime
from peewee import *
import os
# db = MySQLDatabase(host = 'localhost', user = 'root', passwd = 'qwer1234', database = 'test', charset = 'utf8')
db = SqliteDatabase('lock.db')


class QueueModel(Model):
    var = CharField(max_length=30)

    @staticmethod
    def pop():
        items = QueueModel.select()
        if len(items) == 0:
            return None
        res = items[0]
        deleteData = QueueModel.delete().where(QueueModel.id == res.id)  # 使用peewee删除对应的行
        deleteData.execute()  # 执行命令
        # print(len(items))
        return res.var

    @staticmethod
    def push(var):
        item = QueueModel(var=var)
        item.save()
        return item
    class Meta:
        database = db


if __name__ == "__main__":
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    db.connect()
    if not os.path.exists(os.path.join(BASEDIR, 'lock.db')) or True:
        db.create_tables([QueueModel])
    mock = ["1", "2", "3"]
    for item in mock:
        QueueModel.push(item)
    for item in mock:
        print(QueueModel.pop())
    db.close()