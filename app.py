import atexit
import json
import os
import shutil
import uuid

from apscheduler.scheduler import Scheduler
from flask import Flask, Response, request
from flask.templating import render_template
from werkzeug.utils import secure_filename

from models.req.Req import Req
from models.object_detection.ObjectDetection import ObjectDetection

IGNORE_FILES = (".gitignore",)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg"}

NO_OBJECT_MESSAGE = ["No object was found"]

app = Flask(__name__, static_folder=UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cron = Scheduler(daemon=True)
cron.start()


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")


@app.route("/objective", methods=["GET", "POST"])
def objective():
    return render_template("objective.html")


@app.route("/api/v1/detection", methods=["GET", "POST"])
def object_detection():
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
            precision = request.form.get("precision").strip()
        else:
            allowed = ", ".join(list(ALLOWED_EXTENSIONS)[:-1])
            allowed_last = list(ALLOWED_EXTENSIONS)[-1]
            return render_template(
                "400.html",
                msg=f"Allowed Extensions: {allowed} and {allowed_last}",
            )

    elif request.data:
        filename = hex_string + ".jpg"
        folder = os.path.join(app.config["UPLOAD_FOLDER"], hex_string)
        if not os.path.exists(folder):
            os.mkdir(folder)

        path = os.path.join(folder, filename)
        with open(path, "wb") as file:
            file.write(request.data)
        
        precision = "70.0"

    else:
        return render_template("400.html", msg="File not uploaded")

    if not path:
        return render_template("500.html", msg="No file reached the server")

    
    if precision.strip() == "":
        precision = None
    else:
        try:
            precision = float(precision)
            if precision < 0 or precision > 100:
                return render_template(
                    "400.html", msg="Precision must be between 0 and 100"
                )
        except TypeError:
            return render_template(
                "400.html", msg="Precision must be a number. Use '.' for decimal points"
            )

    try:
        status = 200
        if request.data:
            objects = ObjectDetection(path).run()
            response = {"status": status, "body": objects}
            r = Response(
                response=json.dumps(response),
                status=status,
                mimetype="application/json",
            )
        else:
            objects = ObjectDetection(path, json=False).run()
            req = Req(objects, precision)
            description = req.req() or NO_OBJECT_MESSAGE
            processed = req.save()
            r = render_template(
                "processed.html",
                msg=description,
                original="/" + path,
                processed="/" + processed,
            )
    except Exception as e:
        status = 500
        print("Exception:", e)
        if request.data:
            response = {"status": status, "body": "Internal Server Error"}
            r = Response(
                response=json.dumps(response),
                status=status,
                mimetype="application/json",
            )
        else:
            r = render_template("500.html", msg=e)

    return r


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@cron.interval_schedule(minutes=10)
def job_function():
    for folder in os.listdir(app.config["UPLOAD_FOLDER"]):
        if folder not in IGNORE_FILES:
            folder_path = os.path.join(app.config["UPLOAD_FOLDER"], folder)
            shutil.rmtree(folder_path)


atexit.register(lambda: cron.shutdown(wait=False))

