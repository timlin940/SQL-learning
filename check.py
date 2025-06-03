import psycopg2
from configparser import ConfigParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

try:
 conn = psycopg2.connect(dbname="SQL_learning", user="postgres", password="Ninomae0520", host="localhost")
except : 
    print("資料庫連線錯誤")
cursor = conn.cursor()
difficulty ='Easy'
    # 篩選題目
cursor.execute("SELECT title,description FROM question WHERE difficulty = (%s)",(difficulty,))
conn.commit()
questions= cursor.fetchall()
# print(i[0][2])
for q in questions:
   print(q[1])