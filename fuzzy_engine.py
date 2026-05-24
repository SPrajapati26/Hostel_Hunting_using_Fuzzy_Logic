import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import os


class FuzzyRecommender:


    # Traveler profile weights
    WEIGHTS = {
        'backpacker': {
            'value': 0.30,
            'convenience': 0.20,
            'experience': 0.30,
            'safety': 0.22
        },
        'social': {
            'value': 0.18,
            'convenience': 0.18,
            'experience': 0.46,
            'safety': 0.18
        },
        'safety_first': {
            'value': 0.15,
            'convenience': 0.25,
            'experience': 0.15,
            'safety': 0.55
        }
    }

    def __init__(self, csv_path: str = 'data/bern_hostel_complete_dataset.csv'):
        # CSV Location
        paths_to_try = [
            csv_path,
            os.path.abspath(csv_path),
            os.path.join(os.path.dirname(__file__), csv_path),
        ]

        df = None
        for path in paths_to_try:
            try:
                if os.path.exists(path):
                    print(f"  📖 Loading from: {path}")
                    df = pd.read_csv(path, encoding='utf-8')
                    break
            except Exception as e:
                print(f"  ✗ Failed to load from {path}: {e}")
                continue

        if df is None:
            raise FileNotFoundError(f"Could not find CSV at any of these paths: {paths_to_try}")

        self.df = df
        self.hostels = self.df.to_dict('records')
        print(f"  ✓ Successfully loaded {len(self.hostels)} hostels")

    # MEMBERSHIP FUNCTIONS

    @staticmethod
    def trapezoid(x: float, a: float, b: float, c: float, d: float) -> float:
        """Trapezoid membership function"""
        if x <= a or x >= d:
            return 0.0
        elif x >= b and x <= c:
            return 1.0
        elif x < b:
            return (x - a) / (b - a) if b > a else 0.0
        else:
            return (d - x) / (d - c) if d > c else 0.0

    @staticmethod
    def triangle(x: float, a: float, b: float, c: float) -> float:
        """Triangle membership function"""
        if x <= a or x >= c:
            return 0.0
        elif x == b:
            return 1.0
        elif x < b:
            return (x - a) / (b - a) if b > a else 0.0
        else:
            return (c - x) / (c - b) if c > b else 0.0

    # FUZZIFICATION

    def fuzzify_price(self, price: float) -> Dict[str, float]:
        return {
            'low': self.trapezoid(price, 0, 0, 25, 40),
            'med': self.triangle(price, 25, 45, 65),
            'high': self.trapezoid(price, 55, 70, 100, 100)
        }

    def fuzzify_distance(self, distance: float) -> Dict[str, float]:
        return {
            'near': self.trapezoid(distance, 0, 0, 1.5, 3),
            'mod': self.triangle(distance, 1.5, 3.5, 5.5),
            'far': self.trapezoid(distance, 4, 6, 10, 10)
        }

    def fuzzify_rating(self, rating: float) -> Dict[str, float]:
        return {
            'low': self.trapezoid(rating, 0, 0, 5, 7),
            'med': self.triangle(rating, 5, 7, 9),
            'high': self.trapezoid(rating, 7.5, 9, 10, 10)
        }

    #  COMPONENT SCORING

    def compute_value_score(self, hostel: Dict, preference: Dict,
                            fuzz_price: Dict, bonus_breakfast: float) -> float:
        budget = preference['budget']
        budget_fit = max(0, 1 - max(0, (hostel['Budget_per_Night_EUR'] - budget) / budget))

        value_score = (fuzz_price['low'] * 1.0 +
                       fuzz_price['med'] * 0.65 +
                       fuzz_price['high'] * 0.2) * 0.5 + budget_fit * 0.5

        value_score = min(1.0, value_score + bonus_breakfast)
        return float(value_score)

    def compute_convenience_score(self, hostel: Dict, preference: Dict,
                                  fuzz_dist: Dict, bonus_station: float) -> float:
        conv_score = (fuzz_dist['near'] * 1.0 +
                      fuzz_dist['mod'] * 0.6 +
                      fuzz_dist['far'] * 0.15)

        conv_score = min(1.0, conv_score + bonus_station)
        return float(conv_score)

    def compute_experience_score(self, hostel: Dict, preference: Dict,
                                 fuzz_social: Dict, fuzz_wifi: Dict) -> float:
        # Normalize importance from 1-10 to 0-1
        social_importance = max(0, min(1.0, (preference['socialImportance'] - 1) / 9.0))
        wifi_importance = max(0, min(1.0, (preference['wifiImportance'] - 1) / 9.0))

        # base score calculations
        social_score = (fuzz_social['low'] * 0.1 +
                        fuzz_social['med'] * 0.6 +
                        fuzz_social['high'] * 1.0)

        wifi_score = (fuzz_wifi['low'] * 0.2 +
                      fuzz_wifi['med'] * 0.6 +
                      fuzz_wifi['high'] * 1.0)

        # Boost scores based on importance
        social_score = social_score * (0.7 + social_importance * 0.3)
        wifi_score = wifi_score * (0.7 + wifi_importance * 0.3)

        # Dynamic proportion based on importance
        if social_importance + wifi_importance > 0:
            social_weight = social_importance / (social_importance + wifi_importance)
            wifi_weight = wifi_importance / (social_importance + wifi_importance)
        else:
            social_weight = 0.55
            wifi_weight = 0.45

        experience_score = social_score * social_weight + wifi_score * wifi_weight
        return float(min(1.0, experience_score))

    def compute_safety_score(self, hostel: Dict, preference: Dict,
                             fuzz_safety: Dict, fuzz_clean: Dict) -> float:

        safety_component = (fuzz_safety['low'] * 0.05 +
                            fuzz_safety['med'] * 0.5 +
                            fuzz_safety['high'] * 1.0)

        clean_component = (fuzz_clean['low'] * 0.2 +
                           fuzz_clean['med'] * 0.6 +
                           fuzz_clean['high'] * 1.0)

        safety_score = safety_component * 0.65 + clean_component * 0.35
        return float(safety_score)

    # FUZZY RULES & DEFUZZIFICATION

    def evaluate_fuzzy_rules(self, hostel: Dict, fuzz_price: Dict,
                             fuzz_dist: Dict, fuzz_safety: Dict,
                             fuzz_clean: Dict, fuzz_social: Dict,
                             fuzz_wifi: Dict) -> float:
        """Evaluate 10 fuzzy inference rules using Centre-of-Gravity defuzzification"""

        rules = [
            (min(fuzz_price['low'], fuzz_safety['high']), 0.90),
            (min(fuzz_price['low'], fuzz_safety['med']), 0.75),
            (min(fuzz_price['high'], fuzz_dist['far']), 0.08),
            (fuzz_safety['low'], 0.04),
            (min(fuzz_clean['high'], fuzz_safety['high']), 0.90),
            (min(fuzz_social['high'], fuzz_price['low']), 0.85),
            (min(fuzz_dist['near'], fuzz_price['low']), 0.88),
            (min(fuzz_dist['near'], fuzz_safety['high']), 0.84),
            (min(fuzz_price['med'], fuzz_clean['high']), 0.72),
            (min(fuzz_social['high'], fuzz_clean['high']), 0.82)
        ]

        # defuzzification
        numerator = sum(antecedent * consequent for antecedent, consequent in rules)
        denominator = sum(antecedent for antecedent, _ in rules)

        if denominator == 0:
            return 0.5

        return float(numerator / denominator)

    # EXPLANATIONS

    def generate_explanations(self, hostel: Dict, preference: Dict) -> Tuple[List[str], List[str]]:
        """Generate pro and warning tags"""
        good = []
        warn = []

        if hostel['Budget_per_Night_EUR'] <= preference['budget']:
            good.append(f"Within €{preference['budget']} budget")
        else:
            over = hostel['Budget_per_Night_EUR'] - preference['budget']
            warn.append(f"€{over:.0f} over budget")

        if hostel['Safety_Rating_10'] >= 8.5:
            good.append(f"High safety ({hostel['Safety_Rating_10']}/10)")
        elif hostel['Safety_Rating_10'] < 6.5:
            warn.append(f"Low safety ({hostel['Safety_Rating_10']}/10)")

        if hostel['Cleanliness_Rating_10'] >= 8.5:
            good.append(f"Very clean ({hostel['Cleanliness_Rating_10']}/10)")
        elif hostel['Cleanliness_Rating_10'] < 6.5:
            warn.append("Cleanliness concerns")

        if hostel['Distance_from_Centre_km'] <= 1.5:
            good.append(f"Very central ({hostel['Distance_from_Centre_km']}km)")
        elif hostel['Distance_from_Centre_km'] > 5:
            warn.append(f"Far from centre ({hostel['Distance_from_Centre_km']}km)")

        if hostel['Social_Vibe_Score_10'] >= 8.5:
            good.append("Great social vibe")

        if hostel['WiFi_Quality_10'] >= 8.5:
            good.append("Fast WiFi")

        if hostel['Breakfast_Included'] == 'Yes' and preference['wants_breakfast']:
            good.append("Breakfast included")

        if hostel['Nearest_Station_Available'] == 'Yes' and preference['wants_station']:
            good.append("Station nearby")

        return good, warn

    # MAIN FUZZY SCORING

    def score_hostel(self, hostel: Dict, traveler_type: str,
                     preference: Dict) -> Dict[str, Any]:
        """Score a single hostel"""

        weights = self.WEIGHTS[traveler_type]

        fuzz_price = self.fuzzify_price(hostel['Budget_per_Night_EUR'])
        fuzz_dist = self.fuzzify_distance(hostel['Distance_from_Centre_km'])
        fuzz_safety = self.fuzzify_rating(hostel['Safety_Rating_10'])
        fuzz_clean = self.fuzzify_rating(hostel['Cleanliness_Rating_10'])
        fuzz_social = self.fuzzify_rating(hostel['Social_Vibe_Score_10'])
        fuzz_wifi = self.fuzzify_rating(hostel['WiFi_Quality_10'])

        bonus_breakfast = 0.07 if (hostel['Breakfast_Included'] == 'Yes' and preference['wants_breakfast']) else 0
        bonus_station = 0.07 if (hostel['Nearest_Station_Available'] == 'Yes' and preference['wants_station']) else 0

        value_score = self.compute_value_score(hostel, preference, fuzz_price, bonus_breakfast)
        conv_score = self.compute_convenience_score(hostel, preference, fuzz_dist, bonus_station)
        exp_score = self.compute_experience_score(hostel, preference, fuzz_social, fuzz_wifi)
        safe_score = self.compute_safety_score(hostel, preference, fuzz_safety, fuzz_clean)

        # 60% weighted layer + 40% fuzzy rules
        layered_score = (value_score * weights['value'] +
                         conv_score * weights['convenience'] +
                         exp_score * weights['experience'] +
                         safe_score * weights['safety'])

        fuzzy_rule_score = self.evaluate_fuzzy_rules(
            hostel, fuzz_price, fuzz_dist, fuzz_safety,
            fuzz_clean, fuzz_social, fuzz_wifi
        )

        final_score = layered_score * 0.6 + fuzzy_rule_score * 0.4

        good, warn = self.generate_explanations(hostel, preference)

        result = {
            'Hostel_ID': int(hostel['Hostel_ID']),
            'Hostel_Name': str(hostel['Hostel_Name']),
            'Area': str(hostel['Area']),
            'Budget_per_Night_EUR': float(hostel['Budget_per_Night_EUR']),
            'Distance_from_Centre_km': float(hostel['Distance_from_Centre_km']),
            'Safety_Rating_10': float(hostel['Safety_Rating_10']),
            'Cleanliness_Rating_10': float(hostel['Cleanliness_Rating_10']),
            'Social_Vibe_Score_10': float(hostel['Social_Vibe_Score_10']),
            'WiFi_Quality_10': float(hostel['WiFi_Quality_10']),
            'Breakfast_Included': str(hostel['Breakfast_Included']),
            'Nearest_Station_Available': str(hostel['Nearest_Station_Available']),
            'final_score': round(float(final_score), 4),
            'subs': {
                'value': round(float(value_score), 4),
                'conv': round(float(conv_score), 4),
                'exp': round(float(exp_score), 4),
                'safe': round(float(safe_score), 4)
            },
            'good': good,
            'warn': warn
        }

        return result

    def recommend(self, traveler_type: str, budget: float, max_distance: float,
                  min_safety: float, min_cleanliness: float, social_importance: float,
                  wifi_importance: float, wants_breakfast: bool,
                  wants_station: bool) -> List[Dict[str, Any]]:
        """Main recommendation function"""

        # Input validation
        if traveler_type not in self.WEIGHTS:
            raise ValueError(f"Invalid traveler type: {traveler_type}")
        if budget < 0 or budget > 100:
            raise ValueError("Budget must be 0-100 EUR")
        if max_distance < 0 or max_distance > 10:
            raise ValueError("Distance must be 0-10 km")
        if min_safety < 0 or min_safety > 10:
            raise ValueError("Safety rating must be 0-10")
        if min_cleanliness < 0 or min_cleanliness > 10:
            raise ValueError("Cleanliness rating must be 0-10")
        if social_importance < 0 or social_importance > 10:
            raise ValueError("Social importance must be 0-10")
        if wifi_importance < 0 or wifi_importance > 10:
            raise ValueError("WiFi importance must be 0-10")

        preference = {
            'budget': budget,
            'maxDist': max_distance,
            'minSafety': min_safety,
            'minClean': min_cleanliness,
            'socialImportance': social_importance,
            'wifiImportance': wifi_importance,
            'wants_breakfast': wants_breakfast,
            'wants_station': wants_station
        }

        filtered = [h for h in self.hostels
                    if h['Safety_Rating_10'] >= min_safety and
                    h['Cleanliness_Rating_10'] >= min_cleanliness and
                    h['Distance_from_Centre_km'] <= max_distance and
                    (not wants_breakfast or h['Breakfast_Included'] == 'Yes') and
                    (not wants_station or h['Nearest_Station_Available'] == 'Yes')]


        scored = [self.score_hostel(h, traveler_type, preference) for h in filtered]
        ranked = sorted(scored, key=lambda x: x['final_score'], reverse=True)

        return ranked
