
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def div():
    a = int(request.args.get('a', 0))
    b = int(request.args.get('b', 1))
    if b == 0:
        return jsonify(operation='division', error='Cannot divide by zero')
    return jsonify(operation='division', result=a / b)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
