from flask import Flask

from db import RedisClient
from conf import REDIS_VALID_SET_NAME

app = Flask(__name__)
rediscli = RedisClient(setname=REDIS_VALID_SET_NAME)

@app.route('/get', methods=['GET'])
def getOne():
    return rediscli.get()

@app.route('/getall', methods=['GET'])
def getAll():
    return str('\n'.join(rediscli.get_all()))

@app.route('/count', methods=['GET'])
def count():
    return str(rediscli.size)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)