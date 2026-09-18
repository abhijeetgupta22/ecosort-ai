"""
EcoSort AI - Flask Application & API Server
1M1B AI for Sustainability Virtual Internship Project
In Collaboration with IBM SkillsBuild & AICTE
"""

import os
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from core.classifier import WasteClassifier
from core.rag_engine import GraniteRAGEngine
from core.impact_calculator import ImpactCalculator
from core.responsible_ai import ResponsibleAIGovernance

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Core AI Components
classifier = WasteClassifier()
rag_engine = GraniteRAGEngine()
impact_calc = ImpactCalculator()
governance = ResponsibleAIGovernance()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/presentation')
def presentation():
    return render_template('presentation.html')

@app.route('/api/samples', methods=['GET'])
def get_samples():
    """Return list of sample test items."""
    samples = [
        {
            "id": "pet_bottle",
            "name": "PET Water Bottle",
            "image": "/static/sample_images/pet_bottle.png",
            "hint": "Clean transparent beverage bottle"
        },
        {
            "id": "greasy_pizza_box",
            "name": "Greasy Pizza Box",
            "image": "/static/sample_images/greasy_pizza_box.png",
            "hint": "Corrugated cardboard with cheese oil saturation"
        },
        {
            "id": "banana_peel",
            "name": "Organic Banana Peel",
            "image": "/static/sample_images/banana_peel.png",
            "hint": "Fruit peel kitchen scraps"
        },
        {
            "id": "lithium_battery",
            "name": "18650 Li-Ion Battery",
            "image": "/static/sample_images/lithium_battery.png",
            "hint": "Spent rechargeable electronic cell"
        },
        {
            "id": "aluminum_can",
            "name": "Beverage Aluminum Can",
            "image": "/static/sample_images/aluminum_can.png",
            "hint": "Crushed cold drink can"
        },
        {
            "id": "broken_glass",
            "name": "Fractured Glass Jar",
            "image": "/static/sample_images/broken_glass.png",
            "hint": "Broken glass food container"
        }
    ]
    return jsonify({"samples": samples})

@app.route('/api/classify', methods=['POST'])
def classify():
    """Classify a sample item or uploaded image."""
    data = request.json or {}
    sample_id = data.get('sample_id')
    user_hint = data.get('hint', '')

    if sample_id:
        result = classifier.classify_sample(sample_id)
        image_url = f"/static/sample_images/{sample_id}.png"
    else:
        # Check uploaded file
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                ext = Path(file.filename).suffix or '.png'
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(saved_path)
                result = classifier.classify_image(saved_path, user_hint=user_hint)
                image_url = f"/static/uploads/{unique_filename}"
            else:
                return jsonify({"error": "No image file provided"}), 400
        else:
            return jsonify({"error": "Please select a sample or upload an image"}), 400

    # Calculate environmental impact
    impact = impact_calc.calculate_item_impact(result['category_key'], result['weight_grams'])

    # Perform Responsible AI Audit
    responsible_audit = governance.audit_classification(result)

    return jsonify({
        "classification": result,
        "impact": impact,
        "responsible_ai": responsible_audit,
        "image_url": image_url
    })

@app.route('/api/rag_chat', methods=['POST'])
def rag_chat():
    """Process user question through IBM Granite RAG Engine."""
    data = request.json or {}
    query = data.get('query', '').strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    rag_result = rag_engine.query_granite(query)
    return jsonify(rag_result)

@app.route('/api/impact_summary', methods=['GET'])
def impact_summary():
    """Get cumulative campus and session impact numbers."""
    return jsonify(impact_calc.get_session_summary())

@app.route('/api/responsible_governance', methods=['GET'])
def responsible_governance():
    """Return full governance matrix and compliance standards."""
    return jsonify(governance.get_governance_report())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[*] EcoSort AI server running on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
