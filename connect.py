from configparser import ConfigParser
from langchain_google_genai import ChatGoogleGenerativeAI
import psycopg2

def gemini():
    config = ConfigParser()
    config.read("config.ini")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=config["Gemini"]["API_KEY"],
        convert_system_message_to_human=True,
    )
    return llm

def postgres():
    try:
        conn = psycopg2.connect(dbname="SQL_learning", user="postgres", password="Ninomae0520", host="localhost")
        return conn
    except : 
        print("資料庫連線錯誤")