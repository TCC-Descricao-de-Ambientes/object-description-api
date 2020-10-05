import uuid
import os
import json

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

    try:
        objects = SsdMobileNet(path).run()
        response = {'body': str(objects.objects[0])}
    except Exception as e:
        response = {'body': e}
    finally:
        os.remove(path)
        
    return Response(response=json.dumps(response), status=200, mimetype="application/json")
