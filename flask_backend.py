#這邊撰寫flask專用的route等等
from flask import Flask, request, jsonify
import psycopg2
  # 假設 Gemini API 透過OpenAI介面

app = Flask(__name__)

# PostgreSQL 連線設定
conn = psycopg2.connect(dbname="testdb", user="user", password="password", host="localhost")

@app.route('/run_sql', methods=['POST'])
def run_sql():
    sql_query = request.json.get('query')
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            if cur.description:
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                return jsonify({'success': True, 'columns': columns, 'rows': rows})
            else:
                return jsonify({'success': True, 'message': 'Query executed successfully, no result set.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_hint', methods=['POST'])
def get_hint():
    question_desc = request.json.get('question')
    user_sql = request.json.get('query')

    prompt = f"""
    You are an SQL tutor. The student is working on this question:

    {question_desc}

    The student's current SQL query is:

    {user_sql}

    Please provide hints and explanations on how to improve the query, including common pitfalls, syntax tips, and understanding the question. Do NOT give the full answer or complete SQL code.
    """

    # 以 OpenAI GPT API 為範例呼叫 Gemini
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # 更換成你使用的 Gemini 模型名稱
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    advice = response.choices[0].message.content
    return jsonify({'advice': advice})

if __name__ == '__main__':
    app.run(debug=True)