import uuid
import os
import json

from flask import Flask, request, Response, send_from_directory
from flask.templating import render_template
from werkzeug.utils import secure_filename

from models.ssd_mobilenet.SsdMobileNet import SsdMobileNet
from models.req.Req import Req

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/v1/mobilenet", methods=["POST"])
def mobilenet():
    path = None
    hex_string = str(uuid.uuid4().hex)
    if "upload_image" in request.files:
        file = request.files["upload_image"]
        if not file.filename:
            return render_template("400.html", msg="No selected file")

        if file and file.filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
            filename = secure_filename(file.filename)

            folder = os.path.join(app.config["UPLOAD_FOLDER"], hex_string)
            if not os.path.exists(folder):
                os.mkdir(folder)

            path = os.path.join(folder, filename)
            file.save(path)

    elif request.data:
        filename = hex_string + ".jpg"
        folder = os.path.join(app.config["UPLOAD_FOLDER"], hex_string)
        if not os.path.exists(folder):
            os.mkdir(folder)

        path = os.path.join(folder, filename)
        with open(path, "wb") as file:
            file.write(request.data)
    
    else:
        return render_template("400.html", msg="File not uploaded")

    if not path:
        return render_template("500.html", msg="No file reached the server")

    try:
        status = 200
        if request.data:
            objects = SsdMobileNet(path).run()
            response = {"status": status, "body": objects}
        else:
            objects = SsdMobileNet(path, json=False).run()
            req = Req(objects=objects)
            description = req.req()
            processed = req.save()
            return render_template(
                "processed.html",
                msg=description,
                original= "/" + path,
                processed= "/" + processed
            )
    except Exception as e:
        status = 500
        print("Exception:", e)
        if request.data:
            response = {"status": status, "body": "Internal Server Error"}
        else:
            return render_template("500.html", msg=e)
    finally:
        os.remove(path)

    return Response(
        response=json.dumps(response), status=status, mimetype="application/json"
    )


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

