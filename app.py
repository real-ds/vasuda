from flask import Flask, request, jsonify, render_template
import statistics

app = Flask(__name__)

# Store readings only for the current test
readings = []

@app.route("/")
def index():
    return render_template("index.html")


# 🔹 Start a fresh test (called when user clicks Start Test)
@app.route("/start-test", methods=["POST"])
def start_test():
    global readings
    readings = []  # CLEAR previous readings
    return jsonify({"status": "test_started"})


# 🔹 Receive data from ESP32
@app.route("/data", methods=["POST"])
def receive_data():
    global readings
    data = request.json

    # Record ONLY first 10 readings after test starts
    if len(readings) < 10:
        readings.append(data)

    return jsonify({"status": "received"})

@app.route("/latest")
def latest():
    if not readings:
        return jsonify({})
    return jsonify(readings[-1])

# 🔹 Provide summary for dashboard
@app.route("/summary")
def summary():
    # Still recording
    if len(readings) < 10:
        return jsonify({
            "count": len(readings)
        })

    # Compute averages
    avg = lambda key: round(statistics.mean([r[key] for r in readings]), 2)

    avg_ph = avg("soil_ph")
    avg_temp = avg("soil_temp")
    avg_moisture = avg("soil_moisture")
    avg_humidity = avg("air_humidity")

    # Simple Soil Health Risk Score (0 = best, 100 = worst)
    risk = 0
    if avg_ph < 5.5 or avg_ph > 7.5:
        risk += 30
    if avg_moisture < 30:
        risk += 30
    if avg_temp > 35:
        risk += 20
    if avg_humidity < 40:
        risk += 20

    return jsonify({
        "count": 10,
        "avg_ph": avg_ph,
        "avg_temp": avg_temp,
        "avg_moisture": avg_moisture,
        "avg_humidity": avg_humidity,
        "risk_score": min(risk, 100)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)