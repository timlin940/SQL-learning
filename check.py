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

cursor.execute("SELECT * FROM history")
i = cursor.fetchall()
print(i)