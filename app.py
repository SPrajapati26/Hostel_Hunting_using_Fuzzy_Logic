from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from fuzzy_engine import FuzzyRecommender
import os
import traceback

app = Flask(__name__, template_folder='templates')
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for all routes
CORS(app)

try:
    fuzzy_rec = FuzzyRecommender()
    print("✓ Fuzzy recommender initialized successfully")
    print(f"✓ Loaded {len(fuzzy_rec.hostels)} hostels from dataset")
except Exception as e:
    print(f"✗ Error initializing fuzzy recommender: {e}")
    fuzzy_rec = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/dataset', methods=['GET'])
def get_dataset():

    try:
        if not fuzzy_rec:
            return jsonify({'success': False, 'error': 'Recommender not initialized'}), 500

        return jsonify({
            'success': True,
            'count': len(fuzzy_rec.hostels),
            'hostels': fuzzy_rec.hostels
        })
    except Exception as e:
        print(f"Error in /api/dataset: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/hostels', methods=['POST'])
def rank_hostels():
    """Ranked hostels """
    try:
        if not fuzzy_rec:
            return jsonify({'success': False, 'error': 'Recommender not initialized'}), 500

        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400

        # Validate input fields exist
        required_fields = ['type', 'budget', 'maxDist', 'minSafety', 'minClean',
                           'socialImportance', 'wifiImportance', 'breakfast', 'station']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({'success': False, 'error': f'Missing fields: {missing}'}), 400


        if data['type'] not in ['backpacker', 'social', 'safety_first']:
            return jsonify({'success': False, 'error': f'Invalid traveler type: {data["type"]}'}), 400


        try:
            budget = float(data['budget'])
            max_dist = float(data['maxDist'])
            min_safety = float(data['minSafety'])
            min_clean = float(data['minClean'])
            social_imp = float(data['socialImportance'])
            wifi_imp = float(data['wifiImportance'])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid numeric input'}), 400

        # Validate numeric ranges
        if not (18 <= budget <= 75):
            return jsonify({'success': False, 'error': 'Budget must be 18-75 EUR'}), 400
        if not (0.5 <= max_dist <= 7.5):
            return jsonify({'success': False, 'error': 'Distance must be 0.5-7.5 km'}), 400
        if not (1 <= min_safety <= 10):
            return jsonify({'success': False, 'error': 'Safety rating must be 1-10'}), 400
        if not (1 <= min_clean <= 10):
            return jsonify({'success': False, 'error': 'Cleanliness rating must be 1-10'}), 400
        if not (1 <= social_imp <= 10):
            return jsonify({'success': False, 'error': 'Social importance must be 1-10'}), 400
        if not (1 <= wifi_imp <= 10):
            return jsonify({'success': False, 'error': 'WiFi importance must be 1-10'}), 400


        try:
            breakfast = bool(data['breakfast'])
            station = bool(data['station'])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid boolean input'}), 400

        print(f"\n🔍 Processing recommendation request:")
        print(f"  Type: {data['type']}")
        print(f"  Budget: €{budget}")
        print(f"  Max Distance: {max_dist}km")
        print(f"  Min Safety: {min_safety}/10")
        print(f"  Min Cleanliness: {min_clean}/10")
        print(f"  Social Importance: {social_imp}/10")
        print(f"  WiFi Importance: {wifi_imp}/10")
        print(f"  Breakfast: {breakfast}")
        print(f"  Station: {station}")


        ranked_hostels = fuzzy_rec.recommend(
            traveler_type=data['type'],
            budget=budget,
            max_distance=max_dist,
            min_safety=min_safety,
            min_cleanliness=min_clean,
            social_importance=social_imp,
            wifi_importance=wifi_imp,
            wants_breakfast=breakfast,
            wants_station=station
        )

        print(f"  ✓ Returned {len(ranked_hostels)} hostels")

        return jsonify({
            'success': True,
            'count': len(ranked_hostels),
            'hostels': ranked_hostels
        })

    except Exception as e:
        print(f"\n✗ Error in /api/hostels: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

"""Handling of  errors"""
@app.errorhandler(404)
def not_found(e):

    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):

    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🏨 Hostel Hunter - Fuzzy Recommender System")
    print("=" * 60)
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📂 CSV path: {os.path.abspath('data/bern_hostel_complete_dataset.csv')}")
    print(f"📂 CSV exists: {os.path.exists('data/bern_hostel_complete_dataset.csv')}")
    print("=" * 60)
    print("Starting Flask server on http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, port=5000, use_reloader=False)
