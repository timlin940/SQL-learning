#這邊撰寫flask專用的route等等
from flask import Flask, request, render_template
import psycopg2
from configparser import ConfigParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

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

#輸入難度，顯示題目(需要留空間給撰寫程式碼和給意見)
@app.route('/', methods=['GET'])
def index():
    cursor = conn.cursor()
    # 預設難度為 Easy
    difficulty = request.args.get('difficulty', 'Easy')
    # 篩選題目
    cursor.execute("SELECT title,description FROM question WHERE difficulty = (%s)",(difficulty,))
    conn.commit()
    questions= cursor.fetchall()

    return render_template('index.html', questions= questions, selected_difficulty=difficulty)

if __name__ == '__main__':
    app.run(debug=True)

# @app.route('/run_sql', methods=['POST'])
# def run_sql():
#     sql_query = request.json.get('query')
#     try:
#         with conn.cursor() as cur:
#             cur.execute(sql_query)
#             if cur.description:
#                 rows = cur.fetchall()
#                 columns = [desc[0] for desc in cur.description]
#                 return jsonify({'success': True, 'columns': columns, 'rows': rows})
#             else:
#                 return jsonify({'success': True, 'message': 'Query executed successfully, no result set.'})
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)})

# @app.route('/get_hint', methods=['POST'])
# def get_hint():
#     question_desc = request.json.get('question')
#     user_sql = request.json.get('query')

#     prompt = f"""
#     You are an SQL tutor. The student is working on this question:

#     {question_desc}

#     The student's current SQL query is:

#     {user_sql}

#     Please provide hints and explanations on how to improve the query, including common pitfalls, syntax tips, and understanding the question. Do NOT give the full answer or complete SQL code.
#     """

#     # 以 OpenAI GPT API 為範例呼叫 Gemini
#     messages = [
#         SystemMessage(content=""),
#         HumanMessage(content=f"")
#     ]
#     result = llm.invoke(messages)
#     response = result.content
#     advice = response.choices[0].message.content
#     return jsonify({'advice': advice})
