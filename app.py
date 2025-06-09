#這邊撰寫flask專用的route等等
from flask import Flask, request, render_template
import psycopg2
from configparser import ConfigParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import numpy as np
import json
import re

config = ConfigParser()
config.read("config.ini")
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    google_api_key=config["Gemini"]["API_KEY"],
    convert_system_message_to_human=True,
)

app = Flask(__name__)

# PostgreSQL 連線設定
try:
 conn = psycopg2.connect(dbname="SQL_learning", user="postgres", password="Ninomae0520", host="localhost")
except : 
    print("資料庫連線錯誤")

#輸入難度，顯示題目 標題(之後會跳轉到題目頁面)
@app.route('/', methods=['GET'])#首頁
def index():
    cursor = conn.cursor()
    # 預設難度為 Easy
    difficulty = request.args.get('difficulty', 'Easy')
    # 篩選題目
    cursor.execute("SELECT id , title, description FROM question WHERE difficulty = (%s)",(difficulty,))
    questions= cursor.fetchall()

    return render_template('index.html', questions= questions, selected_difficulty=difficulty)

@app.route('/question/<int:q_id>')#顯示題目和作答區
def show_question(q_id):
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM question WHERE id = (%s)",(q_id,))
    result = cursor.fetchone()
    return render_template('question.html',descriptions = result)

def ai_get_hint(question_desc,  type,user_sql=None ):#給AI題目分析
    if type == 0:#給AI題目分析
        prompt = f"""
        You are a helpful SQL tutor. The student is working on this question:

        {question_desc}

        The student's current SQL query is:

        {user_sql}

        When evaluating, please ignore style differences such as keyword case, whitespace, and punctuation style.
        """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"If student's sql is correct, return Answer is correct ,else provide hints and explanations on how to improve the query, without giving the full answer or code.  Please provide hints with line breaks every 80 characters or at logical sentence breaks.")
        ]
        result = llm.invoke(messages)
        response = result.content
    elif type==1:#生成新題目
        prompt = f"""
        You are an expert SQL problem setter.

        Given the following SQL problem description, including the table schema and example data, please create a new SQL problem that:
        - Has similar difficulty and concepts
        - Uses different table names, column names, or data values
        - Alters conditions or requirements to make it a new, unseen variant
        - Does NOT copy the original wording or structure verbatim
        - Provides a clear problem statement, table schema, and example input/output

        Here is the original problem:

        {question_desc}

        Please generate the new problem text in JSON format with one fields: "description".

        Example output:
        {{
        "description": "Detailed problem description including schema and examples."
        }}
        """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content="""
                        Please return ONLY a valid JSON object with properly escaped characters.
                        The JSON must be parsable by standard JSON parsers.
                        Escape all special characters such as newlines, quotes, and backslashes.""")
        ]
        result = llm.invoke(messages)
        response = result.content
    return response
    
@app.route('/run_sql', methods=['POST'])#執行作答區
def run_sql():
    description = request.form.get('description')
    sql_code = request.form.get('sql_code')
    action = request.form.get('action')

    if action == 'run':
        try:
            ai_hint = ai_get_hint(description, 0,sql_code)#如果type = 0，代表做AI_Hint

            result_text = ai_hint

            return render_template('question.html',
                                descriptions=[description],                               
                                result=result_text,
                                )
        except Exception as e:
            result_text = f"Error: {str(e)}"
            return render_template('question.html',
                                descriptions=[description],
                               
                                result=result_text)
    else:
        return "Invalid action", 400

@app.route('/ai_new_question', methods=['POST'])#執行作答區
def ai_question():#讓AI生成題目
    action = request.form.get('ai_action')
    difficulty = request.args.get('ai_difficulty', 'Easy')
    if action == "run" :
        cursor = conn.cursor()#根據難度找id，取1個
        cursor.execute("SELECT id FROM question WHERE difficulty = %s",(difficulty,))#找id
        q = cursor.fetchall()
        le = len(q)
        q_id = q[0][np.random.randint(0,le)]
        cursor.execute("SELECT id,title, description FROM question WHERE id = %s", (q_id,))
        tem = cursor.fetchone()#選出要給AI吃的題目

        ai_question = ai_get_hint(tem, 1,None)
        ai_question = re.sub(r"```json|```|=====.*?=====", " ", ai_question, flags=re.IGNORECASE).strip()
        data = json.loads(ai_question)
        description = data.get("description")

        return render_template('question.html',descriptions = [description ])
    else:
        return "Invalid action", 400

if __name__ == '__main__':
    app.run(debug=True)

