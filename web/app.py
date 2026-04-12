from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/startup-info', methods=['GET'])
def startup_info():
    return jsonify({'status': 'running', 'timestamp': '2026-04-12T08:50:57Z'})

if __name__ == '__main__':
    app.run()
