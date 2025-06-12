#這邊撰寫flask專用的route等等
from flask import Flask, request, render_template
from langchain_core.messages import HumanMessage, SystemMessage
import numpy as np
import json
import re

import connect

conn = connect.postgres()
llm = connect.gemini()

app = Flask(__name__)
record_id = None#用來運用答題記錄
user_id = None

@app.route('/',methods=['GET'])#登入頁面
def login_page():
    return render_template('login.html')

@app.route('/login',methods=['POST'])#進行登入
def login():
    name = request.form.get("username")
    email = request.form.get("email")
    raw_password = request.form.get("password")
    key = request.form.get("login")
    #如果成功，登入，失敗就擋住
    cursor = conn.cursor()
    if key == "登入":#如果按下登入
        
        cursor.execute("SELECT id FROM users WHERE username = %s and email = %s and password_hash = %s",(name,email,raw_password,))
        global user_id
        user_id = cursor.fetchone()[0] #紀錄現在是誰
        print(user_id)
        if user_id:
            cursor.execute("SELECT id , title, description FROM question WHERE difficulty = 'Easy' ")
            questions= cursor.fetchall()
            cursor.close()
            return render_template('index.html',questions = questions,selected_difficulty= "Easy" )
        else:
            message = "登入錯誤"
            cursor.close()
            return render_template('login.html',message  =message)

@app.route('/register_page',methods=['GET'])#去註冊頁面
def register_page():
    return render_template('register.html')

@app.route('/register',methods=['POST'])#執行註冊
def register():
    name = request.form.get("username")
    email = request.form.get("email")
    raw_password = request.form.get("password")
    key = request.form.get("register")
    cursor = conn.cursor()
    if key == "註冊":#如果按下註冊
        cursor.execute("INSERT INTO users (username, email,password_hash) VALUES (%s ,%s ,%s)",(name,email,raw_password,))
        conn.commit()
        print("註冊成功")
        cursor.close()
        return render_template('login.html',message  ="註冊成功")
    else:
        message = "註冊錯誤"
        cursor.close()
        return render_template('register.html',message = message)

#輸入難度，顯示題目 標題(之後會跳轉到題目頁面)
@app.route('/index', methods=['GET'])#首頁
def index():
    cursor = conn.cursor()
    # 預設難度為 Easy
    difficulty = request.args.get('difficulty', 'Easy')
    # 篩選題目
    cursor.execute("SELECT id , title, description FROM question WHERE difficulty = (%s)",(difficulty,))
    questions= cursor.fetchall()
    cursor.close()
    return render_template('index.html', questions= questions, selected_difficulty=difficulty)

@app.route('/question/<int:q_id>')#顯示題目和作答區
def show_question(q_id):
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM question WHERE id = (%s)",(q_id,))
    result = cursor.fetchone()
    global record_id
    record_id = q_id
    cursor.close()
    return render_template('question.html',descriptions = result)

def ai_get_hint(question_desc,type ,last_hint ,user_sql=None ):
    if type == 0:#給AI題目分析
        prompt = f"""
        You are a helpful SQL tutor. The student is working on this question:

        {question_desc}

        The student's current SQL query is:

        {user_sql}

        This is your last hint:
        {last_hint} .Please learn from your last hint and correctly guide students.

        When evaluating, please ignore style differences such as keyword case, whitespace, and punctuation style.
        """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"""
                Please return the result in JSON format with two fields: "Correct" and "Wrong".
                    Example output:
                    {{
                    
                    "Hint" :"Please provide hints with line breaks every 80 characters or at logical sentence breaks.",
                    "Correct": "True.",
                    "Wrong":"False"
                    }}
                """)]
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
    last_hint = request.form.get('hint')#拿上次A生的建議，防止AI重複給錯的建議
    cursor = conn.cursor()
    global record_id
    global user_id
    print(record_id)
    print(user_id)
    if action == 'run':
        print(last_hint)
        ai_hint = ai_get_hint(description, 0,last_hint,sql_code)#如果type = 0，代表做AI_Hint
        ai_hint = re.sub(r"```json|```|=====.*?=====", " ", ai_hint, flags=re.IGNORECASE).strip()#清除干擾json的字元
        data = json.loads(ai_hint)
        correct = data.get("Correct")
        wrong = data.get("Wrong")
        hint = data.get("Hint")
        print(correct)
        cursor.execute("SELECT id FROM history WHERE user_id = %s and question_id = %s",(user_id,record_id,))
        exists = cursor.fetchone() is not None
        if exists:
            if correct == "True":
                cursor.execute("""
                    UPDATE history
                    SET correct_times = correct_times + 1
                    WHERE user_id = %s AND question_id = %s
                """, (user_id, record_id))
            else:
                cursor.execute("""
                    UPDATE history
                    SET wrong_times = wrong_times + 1
                    WHERE user_id = %s AND question_id = %s
                """, (user_id, record_id))
            conn.commit()
            cursor.close()
            return render_template("question.html",correct = correct,wrong = wrong, hint = hint,descriptions= [description])
        else:
            if correct == "True":
                cursor.execute("""
                    INSERT INTO history (user_id, question_id, correct_times, wrong_times)
                    VALUES (%s, %s, 1, 0)
                """, (user_id, record_id))
            else:
                cursor.execute("""
                    INSERT INTO history (user_id, question_id, correct_times, wrong_times)
                    VALUES (%s, %s, 0, 1)
                """, (user_id, record_id))
            conn.commit()
            cursor.close()
            return render_template("question.html",correct = correct,wrong = wrong, hint = hint,descriptions=[description])
    else:
        cursor.close()
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
        q_id = q[np.random.randint(0,le)]
        cursor.execute("SELECT id,title, description FROM question WHERE id = %s", (q_id,))
        tem = cursor.fetchone()#選出要給AI吃的題目

        ai_question = ai_get_hint(tem, 1,"Not yet give hint.",None)
        ai_question = re.sub(r"```json|```|=====.*?=====", " ", ai_question, flags=re.IGNORECASE).strip()#清除干擾json的字元
        data = json.loads(ai_question)
        description = data.get("description")
        cursor.close()
        return render_template('question.html',descriptions = [description ])
    else:
        cursor.close()
        return "Invalid action", 400

if __name__ == '__main__':
    app.run(debug=True)
