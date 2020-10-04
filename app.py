import uuid
import os

from flask import Flask, request, Response

from models.SsdMobileNet import SsdMobileNet

app = Flask(__name__)

RES_FOLDER = 'resources'

@app.route("/api/v1/mobilenet", methods=["POST"])
def mobilenet():
    hex_string = str(uuid.uuid4().hex)
    filename = f"{hex_string}.jpg"

    path = os.path.join('resources', filename)
    with open(path, "wb") as file:
        file.write(request.data)

    response = SsdMobileNet(path).run()
    
    os.remove(path)
    return Response(response=str(response.objects[0]), status=200, mimetype="application/json")


def create_app():
    global app
    return app