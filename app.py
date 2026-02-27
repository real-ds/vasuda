import os
import statistics
import logging
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai

# -------------------------------------------------
# ENV + GEMINI CLIENT SETUP
# -------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    logging.warning("GEMINI_API_KEY not set — AI features will be disabled")

# -------------------------------------------------
# FLASK APP
# -------------------------------------------------
app = Flask(__name__)

# In-memory storage for current test
readings = []

# COMPONENT 1 — SHRS History (rolling window of last 5)
shrs_history = []

# COMPONENT 3 — Previous practice inputs for escalation detection
previous_practices = {"irrigation": None, "fertilizer": None, "crop": None}

# Test history — stores all past test records
test_history = []

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/homepage")
def homepage():
    return render_template("homepage.html")

# -------------------------------------------------
# BLOG PAGES
# -------------------------------------------------
@app.route("/blog/soil-degradation")
def blog_soil_degradation():
    return render_template("blog.html",
        title="Soil Degradation Prevention",
        badge="Soil Science",
        hero_image="/static/images/blog_soil_degradation.png",
        content="""
        <p><strong>Soil degradation is one of the most pressing environmental challenges of our time, affecting over 33% of the world's agricultural land.</strong> Without proactive monitoring, fertile topsoil erodes at alarming rates — up to 100 times faster than it can naturally regenerate. This silent crisis threatens food security for billions and accelerates climate change by releasing stored carbon into the atmosphere.</p>

        <figure class="blog-image">
            <img src="/static/images/soil_degradation.png" alt="Soil degradation comparison showing cracked, dry earth versus healthy soil">
            <figcaption>Degraded soil (left) vs. healthy, nutrient-rich soil (right) — the difference proactive monitoring makes</figcaption>
        </figure>

        <p>VasuDA tackles this by combining <strong>real-time sensor data with predictive AI models</strong> that identify early warning signs of degradation — nutrient depletion, pH imbalance, moisture loss, and organic matter decline. Instead of reacting after the damage is done, farmers receive actionable alerts weeks or even months in advance, enabling them to intervene with targeted remediation strategies like cover cropping, composting, or adjusted tillage practices.</p>

        <div class="takeaway-box">
            <h3>Key Takeaway</h3>
            <p>Prevention is 10x more cost-effective than remediation. By catching degradation early through continuous monitoring, VasuDA helps farmers save both their soil and their investment — preserving land productivity for future generations.</p>
        </div>

        <p>The technology behind VasuDA's degradation prevention draws on <strong>behavioral analytics</strong> — understanding how farming patterns, weather cycles, and soil biology interact over time. This holistic approach means recommendations aren't generic; they're tailored to each field's unique history and conditions, making regenerative agriculture practical and accessible for every farmer.</p>
        """
    )

@app.route("/blog/water-management")
def blog_water_management():
    return render_template("blog.html",
        title="Water Management Optimization",
        badge="Resource Conservation",
        hero_image="/static/images/blog_water_management.png",
        content="""
        <p><strong>Agriculture accounts for 70% of global freshwater withdrawal, yet nearly 60% of irrigation water is wasted through inefficient practices.</strong> As droughts become more frequent and water tables decline, optimizing irrigation isn't just environmentally responsible — it's essential for farm survival. Smart water management can reduce water usage by up to 40% while actually improving crop health.</p>

        <figure class="blog-image">
            <img src="/static/images/blog_water_management.png" alt="Smart irrigation system with soil moisture sensors">
            <figcaption>Intelligent irrigation adapts in real-time based on soil moisture data from embedded sensors</figcaption>
        </figure>

        <p>VasuDA's moisture monitoring goes beyond simple readings. Our system tracks <strong>soil moisture patterns across multiple depth layers</strong>, correlating them with weather forecasts, crop growth stages, and evapotranspiration rates. The result is precision irrigation scheduling that delivers exactly the right amount of water, exactly when and where it's needed — eliminating both overwatering and drought stress.</p>

        <div class="takeaway-box">
            <h3>Key Takeaway</h3>
            <p>Overwatering doesn't just waste water — it leaches nutrients, promotes fungal diseases, and compacts soil. VasuDA's intelligent moisture tracking helps farmers find the sweet spot, conserving water while building healthier, more resilient soil structure.</p>
        </div>

        <p>The economic impact is significant: farmers using data-driven irrigation typically see <strong>25–35% reduction in water costs</strong> alongside measurable improvements in crop quality. By analyzing historical moisture data alongside yield outcomes, VasuDA continuously refines its recommendations, learning what works best for each specific soil type and crop combination on your farm.</p>
        """
    )

@app.route("/blog/crop-yield")
def blog_crop_yield():
    return render_template("blog.html",
        title="Crop Yield Enhancement",
        badge="Productivity",
        hero_image="/static/images/blog_crop_yield.png",
        content="""
        <p><strong>Healthy soil is the foundation of productive farming — research shows that improving soil organic matter by just 1% can increase crop yields by 10–15%.</strong> Yet most farmers lack the tools to understand what's happening beneath the surface. Without real-time soil data, decisions about planting, fertilizing, and harvesting are based on guesswork rather than science, leaving significant productivity gains on the table.</p>

        <figure class="blog-image">
            <img src="/static/images/blog_crop_yield.png" alt="Data-driven crop yield optimization with soil analytics">
            <figcaption>Real-time soil insights enable farmers to make data-driven decisions that directly boost yields</figcaption>
        </figure>

        <p>VasuDA transforms soil data into <strong>actionable farming intelligence</strong>. By continuously monitoring pH, temperature, moisture, and nutrient levels, our AI engine identifies the specific conditions that maximize yield for your crop type. Whether it's adjusting fertilizer application timing, optimizing planting density, or selecting the best crop variety for your soil profile — every recommendation is backed by real data from your own fields.</p>

        <div class="takeaway-box">
            <h3>Key Takeaway</h3>
            <p>The difference between average and exceptional yields often comes down to timing and precision. VasuDA provides both — real-time monitoring catches issues early, while AI-driven insights ensure every farming decision is optimized for maximum productivity.</p>
        </div>

        <p>Farmers using VasuDA's insights have reported <strong>measurable improvements in both yield quantity and quality</strong>. By understanding the relationship between soil health and crop performance at a granular level, they can invest resources where they'll have the greatest impact — turning soil management from a cost center into a strategic advantage that compounds year over year.</p>
        """
    )

@app.route("/blog/sustainable-practices")
def blog_sustainable_practices():
    return render_template("blog.html",
        title="Sustainable Farming Practices",
        badge="Regenerative Agriculture",
        hero_image="/static/images/blog_sustainable.png",
        content="""
        <p><strong>Regenerative agriculture isn't just a trend — it's a necessity.</strong> Conventional farming practices have degraded one-third of the world's arable land over the past 40 years. The shift to sustainable, regenerative methods is critical, but many farmers hesitate because they lack confidence in new approaches. Without data to guide the transition, the perceived risk of changing established practices feels too high.</p>

        <figure class="blog-image">
            <img src="/static/images/blog_sustainable.png" alt="Sustainable farming cycle showing crop rotation and soil regeneration">
            <figcaption>The regenerative farming cycle: healthier soil leads to better yields, which enables more sustainable practices</figcaption>
        </figure>

        <p>VasuDA removes the guesswork from sustainable farming by providing <strong>evidence-based guidance for every step of the transition</strong>. Our platform monitors how regenerative practices — cover cropping, reduced tillage, composting, crop rotation — are actually improving your soil health in real time. Seeing measurable progress builds confidence and helps farmers stay committed to practices that may take 2–3 seasons to show full results.</p>

        <div class="takeaway-box">
            <h3>Key Takeaway</h3>
            <p>Sustainability and profitability aren't opposites — they're partners. Data shows regenerative farms achieve comparable or better yields within 3–5 years while dramatically reducing input costs. VasuDA makes this transition measurable, manageable, and motivating.</p>
        </div>

        <p>Beyond individual farm benefits, VasuDA helps quantify your contribution to <strong>global sustainability goals</strong> — tracking carbon sequestration, water conservation, and biodiversity improvements. This data isn't just meaningful for the environment; it's increasingly valued by consumers, certifiers, and supply chain partners who prioritize sustainably produced food.</p>
        """
    )


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

    # -------- Environmental Risk (0–100) --------
    env_risk = 0

    if avg_ph < 5.5 or avg_ph > 7.5:
        env_risk += 25

    if avg_moisture < 30:
        env_risk += 25
    elif avg_moisture < 40:
        env_risk += 10

    if avg_temp > 40:
        env_risk += 25
    elif avg_temp > 35:
        env_risk += 10

    if avg_humidity < 35:
        env_risk += 25
    elif avg_humidity < 50:
        env_risk += 10

    return jsonify({
        "count": 10,
        "avg_ph": avg_ph,
        "avg_temp": avg_temp,
        "avg_moisture": avg_moisture,
        "avg_humidity": avg_humidity,
        "soil_condition_risk": env_risk  # practice_risk merged on /ai-recommendation
    })


# -------------------------------------------------
# DETERMINISTIC ADVICE ENGINE (no AI required)
# -------------------------------------------------
def compute_practice_risk(crop, irrigation, fertilizer):
    """Practice-based risk modifier. Fully deterministic."""
    risk = 0
    if irrigation and irrigation.lower() == "daily":
        risk += 10
    if fertilizer and fertilizer.lower() == "weekly":
        risk += 10
    if crop and crop.lower() == "rice":
        risk += 5
    return risk


def generate_structured_advice(avg_ph, avg_temp, avg_moisture, avg_humidity,
                                crop, irrigation, fertilizer):
    """
    Pure deterministic rules → list of actionable advice strings.
    Works fully offline. No API dependency.
    """
    advice = []

    # ---- pH Rules ----
    if avg_ph < 5.5:
        advice.append(
            f"⚠️ **Acidic Soil (pH {avg_ph})**: Apply agricultural lime "
            f"(calcium carbonate) at 2–4 tonnes/hectare to raise pH. "
            f"Retest after 4–6 weeks. Avoid ammonium-based fertilizers "
            f"which further acidify soil."
        )
    elif avg_ph > 7.5:
        advice.append(
            f"⚠️ **Alkaline Soil (pH {avg_ph})**: Apply elemental sulfur "
            f"or gypsum at 1–2 tonnes/hectare. Incorporate organic matter "
            f"(composted manure, peat) to gradually lower pH. Avoid "
            f"over-liming."
        )
    else:
        advice.append(
            f"✅ **Soil pH ({avg_ph})** is within the optimal range "
            f"(5.5–7.5). Maintain current practices."
        )

    # ---- Moisture + Irrigation Rules ----
    if avg_moisture < 30 and (not irrigation or irrigation.lower() != "daily"):
        advice.append(
            f"⚠️ **Low Moisture ({avg_moisture}%)**: Increase irrigation "
            f"frequency. Consider drip irrigation for water efficiency. "
            f"Apply organic mulch (4–6 cm) to reduce evaporation."
        )
    elif avg_moisture < 30 and irrigation and irrigation.lower() == "daily":
        advice.append(
            f"⚠️ **Low Moisture Despite Daily Irrigation ({avg_moisture}%)**: "
            f"Soil may have poor water retention. Add compost or "
            f"coco peat to improve structure. Check for drainage issues."
        )
    elif avg_moisture > 50 and irrigation and irrigation.lower() == "daily":
        advice.append(
            f"⚠️ **Over-Irrigation Detected (Moisture {avg_moisture}%, "
            f"Daily Irrigation)**: Reduce watering frequency to every "
            f"2–3 days. Over-watering leaches nutrients and promotes "
            f"root rot. Switch to scheduled drip irrigation."
        )
    else:
        advice.append(
            f"✅ **Soil Moisture ({avg_moisture}%)** is adequate. "
            f"Continue current irrigation schedule."
        )

    # ---- Temperature Rules ----
    if avg_temp > 40:
        advice.append(
            f"🔥 **Extreme Heat ({avg_temp}°C)**: Apply straw mulch "
            f"(8–10 cm) immediately. Irrigate during early morning "
            f"or late evening. Consider shade netting for sensitive crops."
        )
    elif avg_temp > 35:
        advice.append(
            f"⚠️ **High Temperature ({avg_temp}°C)**: Monitor crop stress "
            f"closely. Increase organic mulch cover. Avoid fertilizer "
            f"application during peak heat to prevent root burn."
        )
    elif avg_temp < 10:
        advice.append(
            f"❄️ **Low Temperature ({avg_temp}°C)**: Risk of frost damage. "
            f"Use row covers or cold frames. Delay planting of warm-season "
            f"crops until soil warms above 15°C."
        )

    # ---- Humidity Rules ----
    if avg_humidity < 35:
        advice.append(
            f"⚠️ **Low Humidity ({avg_humidity}%)**: Increase mulching to "
            f"preserve soil moisture. Consider windbreaks to reduce "
            f"evapotranspiration. Mist irrigation may help in greenhouse "
            f"settings."
        )
    elif avg_humidity > 70 and avg_temp > 28:
        advice.append(
            f"🦠 **Fungal Disease Risk (Humidity {avg_humidity}%, "
            f"Temp {avg_temp}°C)**: Monitor for blight, mildew, and "
            f"rust. Ensure adequate plant spacing for airflow. "
            f"Apply preventive copper-based fungicide if symptoms appear."
        )

    # ---- Fertilizer Rules ----
    if fertilizer and fertilizer.lower() == "weekly":
        advice.append(
            f"⚠️ **Frequent Fertilization (Weekly)**: Risk of nutrient "
            f"buildup and salt stress. Adopt split nitrogen application — "
            f"apply 40% at planting, 30% at tillering, 30% at flowering. "
            f"Conduct soil nutrient tests every 3 months."
        )
    elif fertilizer and fertilizer.lower() == "none":
        advice.append(
            f"⚠️ **No Fertilizer Applied**: Soil nutrient depletion is "
            f"likely over time. Consider a balanced NPK application or "
            f"composted organic manure as a minimum baseline."
        )

    # ---- Crop-Specific Rules ----
    if crop and crop.lower() == "rice":
        advice.append(
            f"🌾 **Rice Cultivation**: Maintain standing water depth of "
            f"2–5 cm during vegetative stage. Alternate wetting and drying "
            f"(AWD) technique saves 15–30% water with no yield loss."
        )

    return advice


# -------------------------------------------------
# COMPONENT 2 — RISK TREND DETECTION
# -------------------------------------------------
def detect_risk_trend():
    """Analyze last 3 SHRS values for trend direction."""
    if len(shrs_history) < 3:
        return "Insufficient Data"
    last_three = shrs_history[-3:]
    if last_three[2] > last_three[1] > last_three[0]:
        return "Increasing Risk"
    elif last_three[2] < last_three[1] < last_three[0]:
        return "Decreasing Risk"
    return "Stable"


# -------------------------------------------------
# COMPONENT 3 — PRACTICE ESCALATION WARNING
# -------------------------------------------------
IRRIGATION_RANK = {
    "irregular": 1, "weekly": 2, "alternate days": 3, "daily": 4
}
FERTILIZER_RANK = {
    "none": 1, "rare": 2, "monthly": 3, "weekly": 4
}

def detect_practice_escalation(current_irrigation, current_fertilizer):
    """Compare current vs. previous practice inputs for escalation."""
    global previous_practices
    warnings = []

    prev_irr = previous_practices.get("irrigation")
    prev_fert = previous_practices.get("fertilizer")

    if prev_irr and current_irrigation:
        old_rank = IRRIGATION_RANK.get(prev_irr.lower(), 0)
        new_rank = IRRIGATION_RANK.get(current_irrigation.lower(), 0)
        if new_rank > old_rank:
            warnings.append(
                f"Irrigation frequency increased ({prev_irr} → {current_irrigation}) "
                f"— monitor water usage and soil saturation."
            )

    if prev_fert and current_fertilizer:
        old_rank = FERTILIZER_RANK.get(prev_fert.lower(), 0)
        new_rank = FERTILIZER_RANK.get(current_fertilizer.lower(), 0)
        if new_rank > old_rank:
            warnings.append(
                f"Fertilizer application intensified ({prev_fert} → {current_fertilizer}) "
                f"— watch for nutrient runoff and salt buildup."
            )

    # Update stored practices for next comparison
    previous_practices["irrigation"] = current_irrigation
    previous_practices["fertilizer"] = current_fertilizer

    return warnings if warnings else None


# -------------------------------------------------
# AI RECOMMENDATION (Deterministic-first, Gemini-polish)
# -------------------------------------------------
@app.route("/ai-recommendation", methods=["POST"])
def ai_recommendation():
    global shrs_history
    data = request.json

    avg_ph = float(data.get("avg_ph", 6.5))
    avg_temp = float(data.get("avg_temp", 25))
    avg_moisture = float(data.get("avg_moisture", 50))
    avg_humidity = float(data.get("avg_humidity", 60))
    crop = data.get("crop", "")
    irrigation = data.get("irrigation", "")
    fertilizer = data.get("fertilizer", "")
    env_risk = int(data.get("risk_score", 0))

    # ---- Step 1: Practice Risk ----
    practice_risk = compute_practice_risk(crop, irrigation, fertilizer)

    # ---- Step 2: Merged SHRS (capped at 100) ----
    shrs = min(env_risk + practice_risk, 100)

    # ---- COMPONENT 1: Store SHRS in rolling history ----
    shrs_history.append(shrs)
    if len(shrs_history) > 5:
        shrs_history = shrs_history[-5:]

    # ---- COMPONENT 2: Trend detection ----
    trend = detect_risk_trend()

    # ---- COMPONENT 3: Practice escalation ----
    practice_warning = detect_practice_escalation(irrigation, fertilizer)

    # ---- Step 3: Deterministic Advice (works offline) ----
    structured_advice = generate_structured_advice(
        avg_ph, avg_temp, avg_moisture, avg_humidity,
        crop, irrigation, fertilizer
    )

    # ---- COMPONENT 4: Build enriched fallback text ----
    fallback_text = f"## Soil Health Risk Score: {shrs}/100\n\n"
    fallback_text += f"**Environmental Risk:** {env_risk} | **Practice Risk:** {practice_risk}\n\n"
    fallback_text += f"📈 **Trend:** {trend}\n\n"
    if practice_warning:
        for pw in practice_warning:
            fallback_text += f"🚨 **Warning:** {pw}\n\n"
    fallback_text += "### Recommendations\n\n"
    for item in structured_advice:
        fallback_text += f"- {item}\n\n"

    # ---- Build the result dict ----
    result = {
        "recommendation": fallback_text,
        "shrs": shrs,
        "trend": trend,
        "practice_warning": practice_warning,
        "shrs_history": shrs_history,
        "source": "deterministic"
    }

    # ---- Try Gemini formatting ----
    if client:
        trend_context = f"\nRisk Trend: {trend}"
        warning_context = ""
        if practice_warning:
            warning_context = "\nPractice Warnings: " + "; ".join(practice_warning)

        prompt = f"""You are an agricultural report formatter.

Below is a pre-analyzed soil health report with a risk score and specific recommendations.
Your job is to REFORMAT and ENRICH the language — make it more readable, professional,
and farmer-friendly. Use markdown formatting with headers and bullet points.

CRITICAL RULES:
- Do NOT add new advice that isn't already in the list below
- Do NOT change the risk score or re-analyze the data
- Keep ALL original recommendations, just improve clarity and formatting
- Include the trend direction and any practice warnings prominently
- Add a brief 1-sentence summary at the top

Soil Health Risk Score: {shrs}/100
Environmental Risk: {env_risk} | Practice Risk: {practice_risk}{trend_context}{warning_context}

Sensor Data (for context only, do NOT re-analyze):
- pH: {avg_ph}, Temp: {avg_temp}°C, Moisture: {avg_moisture}%, Humidity: {avg_humidity}%
- Crop: {crop or 'Not specified'}, Irrigation: {irrigation or 'Not specified'}, Fertilizer: {fertilizer or 'Not specified'}

Pre-Generated Recommendations to format:
{chr(10).join(f"- {a}" for a in structured_advice)}
"""
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            text = response.candidates[0].content.parts[0].text.strip()
            result["recommendation"] = text
            result["source"] = "gemini_formatted"
        except Exception as e:
            logging.warning(f"Gemini formatting failed, returning raw advice: {e}")

    # ---- Save to test history ----
    from datetime import datetime
    record = {
        "id": len(test_history) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sensor": {
            "ph": avg_ph, "temp": avg_temp,
            "moisture": avg_moisture, "humidity": avg_humidity
        },
        "practices": {
            "crop": crop, "irrigation": irrigation, "fertilizer": fertilizer
        },
        "shrs": shrs,
        "env_risk": env_risk,
        "practice_risk": practice_risk,
        "trend": trend,
        "recommendation": result["recommendation"]
    }
    test_history.append(record)

    return jsonify(result)

# -------------------------------------------------
# TEST HISTORY
# -------------------------------------------------
@app.route("/history")
def get_history():
    return jsonify(list(reversed(test_history)))

@app.route("/history/clear", methods=["POST"])
def clear_history():
    global test_history
    test_history = []
    return jsonify({"status": "cleared"})

# -------------------------------------------------
# TRANSLATION ROUTE
# -------------------------------------------------
@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.json
    text = data.get("text")
    language = data.get("language")

    if not text or not language:
        return jsonify({"error": "Missing text or language"}), 400

    if not client:
        return jsonify({"error": "AI service not configured. Set GEMINI_API_KEY."}), 503

    prompt = f"""Translate the following agricultural advisory text into {language}.

Rules:
- Only return the translated text, nothing else
- Preserve bullet points and list formatting
- Keep technical agricultural terms accurate
- Do not add explanations or notes

Text to translate:
{text}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        translated = response.candidates[0].content.parts[0].text.strip()
        return jsonify({"translated": translated})
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)