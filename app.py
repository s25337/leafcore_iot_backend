# app.py

from flask import Flask, render_template, request, jsonify
import devices

app = Flask(__name__)

@app.route("/")
def index():
    temp, hum = devices.read_sensor()
    return render_template("index.html", temperature=temp, humidity=hum)

@app.route("/control", methods=["POST"])
def control():
    data = request.json
    devices.set_fan(data.get("fan", False))
    devices.set_light(data.get("light", False))
    devices.set_pump(data.get("pump", False))
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
