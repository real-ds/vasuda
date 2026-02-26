import os
import statistics
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai

# -------------------------------------------------
# ENV + GEMINI CLIENT SETUP
# -------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------------------------------
# FLASK APP
# -------------------------------------------------
app = Flask(__name__)

# In-memory storage for current test
readings = []

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
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

    # -------- Soil Condition Risk (0–100) --------
    soil_risk = 0

    if avg_ph < 5.5 or avg_ph > 7.5:
        soil_risk += 25

    if avg_moisture < 30:
        soil_risk += 25
    elif avg_moisture < 40:
        soil_risk += 10

    if avg_temp > 40:
        soil_risk += 25
    elif avg_temp > 35:
        soil_risk += 10

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


# -------------------------------------------------
# AI RECOMMENDATION (OFFICIAL GENAI SDK)
# -------------------------------------------------
@app.route("/ai-recommendation", methods=["POST"])
def ai_recommendation():
    data = request.json

    prompt = f"""
You are an agricultural expert.

Provide concise, actionable soil health advice.

Soil Data:
- Soil pH: {data['avg_ph']}
- Soil Temperature: {data['avg_temp']} °C
- Soil Moisture: {data['avg_moisture']} %
- Environment Humidity: {data['avg_humidity']} %

Farmer Inputs:
- Crop: {data['crop']}
- Irrigation: {data['irrigation']}
- Fertilizer: {data['fertilizer']}

Soil Health Risk Score: {data['risk_score']} / 100

Rules:
- Use bullet points
- Keep steps practical
- Avoid long paragraphs
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        # ✅ SAFE PARSING
        text = (
            response.candidates[0]
            .content.parts[0]
            .text.strip()
        )

        return jsonify({"recommendation": text})

    except Exception as e:
        return jsonify({
            "recommendation": "AI could not generate recommendations at this time."
        })
# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)