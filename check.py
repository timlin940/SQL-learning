import psycopg2
from configparser import ConfigParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

try:
 conn = psycopg2.connect(dbname="SQL_learning", user="postgres", password="Ninomae0520", host="localhost")
except : 
    print("資料庫連線錯誤")
cursor = conn.cursor()

# 新增user
# cursor.execute("""
#      CREATE Table users (id SERIAL PRIMARY KEY,
#                           username VARCHAR(50) NOT NULL UNIQUE,
#                           email VARCHAR(100) NOT NULL UNIQUE,
#                           password_hash TEXT NOT NULL,
#                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
#                 """)

# 新增history
# cursor.execute("""CREATE TABLE history( id SERIAL PRIMARY KEY,
#                                         user_id INT NOT NULL ,
#                                         question_id INT, 
#                                         correct_times INT , 
#                                         wrong_times INT  )""")


sql = """
INSERT INTO question (title, description, difficulty)
VALUES (%s, %s, %s)
"""

title = 'Rising Temperature'
description = """Table: Weather

+---------------+---------+
| Column Name   | Type    |
+---------------+---------+
| id            | int     |
| recordDate    | date    |
| temperature   | int     |
+---------------+---------+
id is the column with unique values for this table.
There are no different rows with the same recordDate.
This table contains information about the temperature on a certain day.
 

Write a solution to find all dates' id with higher temperatures compared to its previous dates (yesterday).

Return the result table in any order.

The result format is in the following example.

 

Example 1:

Input: 
Weather table:
+----+------------+-------------+
| id | recordDate | temperature |
+----+------------+-------------+
| 1  | 2015-01-01 | 10          |
| 2  | 2015-01-02 | 25          |
| 3  | 2015-01-03 | 20          |
| 4  | 2015-01-04 | 30          |
+----+------------+-------------+
Output: 
+----+
| id |
+----+
| 2  |
| 4  |
+----+
Explanation: 
In 2015-01-02, the temperature was higher than the previous day (10 -> 25).
In 2015-01-04, the temperature was higher than the previous day (20 -> 30).

"""
difficulty = 'Easy'

cursor.execute(sql, (title, description, difficulty))
conn.commit()



