from flask import Flask

from db import RedisClient
from conf import REDIS_VALID_SET_NAME

app = Flask(__name__)
rediscli = RedisClient(setname=REDIS_VALID_SET_NAME)

@app.route('/get', methods=['GET'])
def getOne():
    return rediscli.get()

if __name__ == '__main__':
    app.run(debug=True)