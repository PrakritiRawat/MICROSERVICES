
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def mul():
    a = int(request.args.get('a', 0))
    b = int(request.args.get('b', 0))
    return jsonify(operation='multiplication', result=a * b)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
