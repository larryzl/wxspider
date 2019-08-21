#!/bin/bash

# 删除migrations文件
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
# 删除__pycache__文件
find . -path "*/__pycache__/*" -delete

# 删除数据库文件
rm -f db.sqlite3

# 生成数据库文件
#python manage.py makemigrations
#python manage.py migrate
