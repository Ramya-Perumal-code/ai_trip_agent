import requests
import json
import os

# Base URL for the GetYourGuide Partner API
# NOTE: Ensure this is the correct production endpoint version
BASE_URL = "https://api.getyourguide.com/1"
API_KEY = os.getenv("GYG_API_KEY", "your_api_key_here")

def get_headers():
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

def search_tours(query, limit=5):
    """
    Searches for tours/activities using the GetYourGuide API.
    Attempts to use the live API if a key is present; otherwise falls back to mock data.
    """
    print(f"Searching for: {query}")
    
    # Check if API key is configured
    if API_KEY == "your_api_key_here" or not API_KEY:
        print("⚠️ GYG_API_KEY not set. Using mock data.")
        return _mock_search_tours(query)

    try:
        # Construct the API URL
        url = f"{BASE_URL}/tours"
        params = {
            "query": query,
            "limit": limit,
            "currency": "USD", 
            "lang": "en"
        }
        
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Assuming the API returns a list under a 'tours' or 'data' key, or is a list itself.
            raw_results = data.get("tours", []) if isinstance(data, dict) else data
            
            # Normalize results to ensure tour_id exists for tool_calls.py
            normalized_results = []
            if isinstance(raw_results, list):
                for item in raw_results:
                    # Try to find ID
                    t_id = item.get("tour_id") or item.get("id") or item.get("activityId")
                    if t_id:
                        item["tour_id"] = t_id
                        normalized_results.append(item)
            
            return normalized_results
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            # Fallback to empty or mock? Return empty to signal failure to find real data
            return []
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []

def _mock_search_tours(query):
    """Fallback mock data for testing without valid API credentials."""
    return [
        {
            "tour_id": "12345",
            "title": "Venice: Grand Canal Gondola Ride",
            "rating": 4.8,
            "reviews": 1200,
            "price": {"amount": 35.00, "currency": "EUR"},
            "duration": "30 minutes"
        },
        {
            "tour_id": "67890",
            "title": "Venice: Doge's Palace Skip-the-Line Tour",
            "rating": 4.7,
            "reviews": 850,
            "price": {"amount": 45.00, "currency": "EUR"},
            "duration": "1 hour"
        }
    ]

def get_tour_details(tour_id):
    """
    Fetches detailed information for a specific tour from the API.
    """
    print(f"Fetching details for tour ID: {tour_id}")

    # Check if API key is configured
    if API_KEY == "your_api_key_here" or not API_KEY:
        return _mock_get_tour_details(tour_id)
        
    try:
        url = f"{BASE_URL}/tours/{tour_id}"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            gyg_raw_data = response.json()
            return _map_to_schema(gyg_raw_data)
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return {}

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {}

def _mock_get_tour_details(tour_id):
    """Fallback mock data."""
    if tour_id == "12345":
        gyg_raw_data = {
            "id": "12345",
            "name": "Venice: Grand Canal Gondola Ride",
            "description": "Experience the magic of restricted waterways...",
            "highlights": ["Glide down the Grand Canal", "See historic palazzos"],
            "inclusions": ["Gondola ride", "Live commentary"],
            "exclusions": ["Food and drink", "Hotel pickup"],
            "meeting_point": "St. Mark's Square, by the column",
            "requirements": ["No large bags"],
            "coordinates": {"lat": 45.434, "lon": 12.339},
            "rating": 4.8,
            "duration_min": 30,
            "know_before_you_go": ["Ride is shared with others", "Weather dependent"]
        }
    else:
        gyg_raw_data = {
            "id": tour_id,
            "name": "Sample Tour",
            "description": "A sample tour description.",
            "highlights": ["Highlight 1"],
            "inclusions": ["Inclusion 1"],
            "exclusions": [],
            "requirements": [],
            "rating": 4.5,
            "duration_min": 60,
             "know_before_you_go": []
        }
    return _map_to_schema(gyg_raw_data)

def _map_to_schema(gyg_raw_data):
    """Maps raw GYG API data to the project's internal schema."""
    return {
        "Attraction_name": gyg_raw_data.get("name") or gyg_raw_data.get("title"),
        "Why visit": gyg_raw_data.get("highlights", []),
        "What included": gyg_raw_data.get("inclusions", []),
        "What not included": gyg_raw_data.get("exclusions", []),
        "Restrictions": gyg_raw_data.get("requirements", []),
        "Location": [f"Meeting Point: {gyg_raw_data.get('meeting_point', 'See ticket')} "],
        "User Rating": f"{gyg_raw_data.get('rating')} stars",
        "Duration": f"{gyg_raw_data.get('duration_min') or gyg_raw_data.get('duration')} minutes",
        "additional Information": gyg_raw_data.get("know_before_you_go", [])
    }

def save_to_dataset(data, filename="gyg_output.json"):
    """
    Saves the formatted data to a JSON file in the dataset_json folder.
    """
    output_dir = "dataset_json"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    full_structure = {
        "success": True,
        "data": {
            "markdown": f"# {data.get('Attraction_name', 'Unknown')}\n\n{data.get('Attraction_name', 'Unknown')}...",
            "metadata": {
                "source": "GetYourGuide API",
                "id": "mock_id" # Should ideally be the real ID
            },
            "json": data
        }
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(full_structure, f, indent=2)
    print(f"Saved to {filepath}")

# Example Usage
if __name__ == "__main__":
    # 1. Search for tours
    results = search_tours("Venice")
    
    if results:
        # 2. Get details for the first result
        first_tour_id = results[0]["tour_id"]
        tour_details = get_tour_details(first_tour_id)
        
        # 3. Print result
        print(json.dumps(tour_details, indent=2))
        
        # 4. Save to file (mimicking the scraper output)
        save_to_dataset(tour_details, "gyg_venice_gondola.json")
