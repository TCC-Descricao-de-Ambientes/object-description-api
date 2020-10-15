import uuid
import os
import json
import atexit
import shutil

from flask import Flask, request, Response
from flask.templating import render_template
from werkzeug.utils import secure_filename
from apscheduler.scheduler import Scheduler

from models.ssd_mobilenet.SsdMobileNet import SsdMobileNet
from models.req.Req import Req

IGNORE_FILES = (".gitignore",)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg"}

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


@app.route("/api/v1/mobilenet", methods=["GET", "POST"])
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

    precision = request.form.get('precision').strip()
    if precision.strip() == '':
        precision = None
    else:
        try:
            precision = float(precision)
            if precision < 0 or precision > 100:
                return render_template("400.html", msg="Precision must be between 0 and 100")
        except TypeError:
            return render_template("400.html", msg="Precision must be a number. Use '.' for decimal points")
    
    try:
        status = 200
        if request.data:
            objects = SsdMobileNet(path).run()
            response = {"status": status, "body": objects}
            r = Response(
                response=json.dumps(response),
                status=status,
                mimetype="application/json",
            )
        else:
            objects = SsdMobileNet(path, json=False).run()
            req = Req(objects, precision)
            description = req.req()
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
