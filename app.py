from flask import Flask, request, jsonify, render_template
import statistics

app = Flask(__name__)
readings = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start-test", methods=["POST"])
def start_test():
    global readings
    readings = []
    return jsonify({"status": "started"})

@app.route("/data", methods=["POST"])
def receive_data():
    global readings
    if len(readings) < 10:
        readings.append(request.json)
    return jsonify({"status": "ok"})

@app.route("/latest")
def latest():
    if not readings:
        return jsonify({})
    return jsonify(readings[-1])

@app.route("/summary")
def summary():
    if len(readings) < 10:
        return jsonify({"count": len(readings)})

    avg = lambda k: round(statistics.mean([r[k] for r in readings]), 2)

    avg_ph = avg("soil_ph")
    avg_temp = avg("soil_temp")
    avg_moisture = avg("soil_moisture")
    avg_humidity = avg("air_humidity")

    # Soil Condition Risk
    soil_risk = 0

    # pH
    if avg_ph < 5.5 or avg_ph > 7.5:
        soil_risk += 25

    # Moisture
    if avg_moisture < 30:
        soil_risk += 25
    elif avg_moisture < 40:
        soil_risk += 10

    # Temperature
    if avg_temp > 40:
        soil_risk += 25
    elif avg_temp > 35:
        soil_risk += 10

    # Humidity
    if avg_humidity < 35:
        soil_risk += 25
    elif avg_humidity < 50:
        soil_risk += 10

    return jsonify({
        "count": 10,
        "avg_ph": avg_ph,
        "avg_temp": avg_temp,
        "avg_moisture": avg_moisture,
        "avg_humidity": avg_humidity,
        "soil_condition_risk": soil_risk
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)