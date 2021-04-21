from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def get_data():
    #print(request.data)
    #print(type(request.data))
    print(request.data.decode('utf-8'))
    #print(json.loads(request.data.decode("utf-8")))

    return 'This is working!'

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0')
