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


# sql = """
# INSERT INTO question (title, description, difficulty)
# VALUES (%s, %s, %s)
# """

# title = 'Customer Who Visited but Did Not Make Any Transactions'
# description = """Table: Visits

# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | visit_id    | int     |
# | customer_id | int     |
# +-------------+---------+
# visit_id is the column with unique values for this table.
# This table contains information about the customers who visited the mall.

# Table: Transactions

# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | transaction_id | int     |
# | visit_id       | int     |
# | amount         | int     |
# +----------------+---------+
# transaction_id is column with unique values for this table.
# This table contains information about the transactions made during the visit_id.

# Write a solution to find the IDs of the users who visited without making any transactions and the number of times they made these types of visits.

# Return the result table sorted in any order.

# Example 1:

# Input: 
# Visits
# +----------+-------------+
# | visit_id | customer_id |
# +----------+-------------+
# | 1        | 23          |
# | 2        | 9           |
# | 4        | 30          |
# | 5        | 54          |
# | 6        | 96          |
# | 7        | 54          |
# | 8        | 54          |
# +----------+-------------+
# Transactions
# +----------------+----------+--------+
# | transaction_id | visit_id | amount |
# +----------------+----------+--------+
# | 2              | 5        | 310    |
# | 3              | 5        | 300    |
# | 9              | 5        | 200    |
# | 12             | 1        | 910    |
# | 13             | 2        | 970    |
# +----------------+----------+--------+
# Output: 
# +-------------+----------------+
# | customer_id | count_no_trans |
# +-------------+----------------+
# | 54          | 2              |
# | 30          | 1              |
# | 96          | 1              |
# +-------------+----------------+

# Explanation: 
# Customer with id = 23 visited the mall once and made one transaction during the visit with id = 12.
# Customer with id = 9 visited the mall once and made one transaction during the visit with id = 13.
# Customer with id = 30 visited the mall once and did not make any transactions.
# Customer with id = 54 visited the mall three times. During 2 visits they did not make any transactions, and during one visit they made 3 transactions.
# Customer with id = 96 visited the mall once and did not make any transactions.
# As we can see, users with IDs 30 and 96 visited the mall one time without making any transactions. Also, user 54 visited the mall twice and did not make any transactions.
# """
# difficulty = 'Easy'

# cursor.execute(sql, (title, description, difficulty))
# conn.commit()



