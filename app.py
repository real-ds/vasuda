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

    if not client:
        return jsonify({"recommendation": "AI service not configured. Set GEMINI_API_KEY."})

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
# TRANSLATION ROUTE
# -------------------------------------------------
@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.json
    text = data.get("text")
    language = data.get("language")

    if not text or not language:
        return jsonify({"error": "Missing text or language"}), 400

    prompt = f"Translate the following agricultural text into {language}. Only return the translated text.\n\nText:\n{text}"

    if not client:
        return jsonify({"error": "AI service not configured"}), 503

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        translated = response.candidates[0].content.parts[0].text.strip()
        return jsonify({"translated": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)