from flask import Flask, request, jsonify
import spacy

app = Flask(__name__)

print("Loading spaCy model (en_core_web_lg)...")
nlp = spacy.load("en_core_web_lg")
print("--- AI Models Loaded (Keyword-Only Mode). Server is ready. ---")

KEYWORD_MAP = {
    # Added 'reconstruction' to Roadwork
    "Road Accident": ["accident", "crash", "collision", "overturned", "flyover", "die on road", "deaths on"],
    "Roadwork": ["construction", "road work", "diversion", "roadblock", "flyover", "reconstruction"],
    "Public Event": ["visit", "protest", "rally", "procession", "strike", "demand pay", "reviews arrangements", "inaugurates"],
    "Explosion": ["explosion", "blast", "firecracker", "seize firecrackers"],
    "Flood": ["flood", "inundated", "waterlogging", "submerged"],
    "Heavy Rain": ["heavy rain", "downpour", "torrential rain"],
    "Fire": ["fire", "blaze"],
    "Protest": ["protest", "agitation", "demonstration", "workers demand", "launches campaign"],
    "Severe Weather": ["cyclone", "hailstorm", "storm", "weather alert", "gale"],
}

def find_locations(text):
    doc = nlp(text)
    
    # --- NEW: Diagnostic Print ---
    # Print all entities found by spaCy so we can see what it's thinking
    print("--- spaCy Entity Analysis ---")
    all_entities = [(ent.text, ent.label_) for ent in doc.ents]
    if all_entities:
        print(all_entities)
    else:
        print("No entities found.")
    # -----------------------------

    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    ignore_list = ["Central", "South", "North", "East", "West", "National"]
    
    final_locations = [loc for loc in locations if loc not in ignore_list]
    print(f"--- Locations Found: {final_locations} ---")
    return final_locations

@app.route('/analyze', methods=['POST'])
def analyze_text():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text_to_classify = data['text']
    text_lower = text_to_classify.lower()
    
    print(f"\n--- Analyzing: '{text_to_classify}'")

    found_classification = None
    for category, keywords in KEYWORD_MAP.items():
        if any(keyword in text_lower for keyword in keywords):
            print(f"!!! KEYWORD MATCH: Found a keyword for category '{category}'")
            found_classification = category
            break

    if found_classification:
        output_data = {
            "is_relevant": True,
            "original_text": text_to_classify,
            "classification": found_classification,
            "locations": find_locations(text_to_classify)
        }
    else:
        print("--- No keyword match found. Ignoring. ---")
        output_data = { "is_relevant": False }
    
    return jsonify(output_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)