"""PlaceRecommender Web Application
@author: Burak Kaya
@email: burak.k3574@gmail.com
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
from openai import OpenAI
import os
import requests
import googlemaps
import pandas as pd
from typing import List, Dict, Optional

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Set API keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MAPS_API_KEY = os.environ.get('MAPS_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_place_details(place_id: str, api_key: str) -> Optional[Dict]:
    """Get place details using Google Places API"""
    URL = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
    response = requests.get(URL)
    if response.status_code == 200:
        result = json.loads(response.content)["result"]
        return result
    else:
        print(f"Google Place Details API request failed with status code {response.status_code}")
        return None

def generate_short_answer(user_input: str) -> str:
    """Generate a short answer using OpenAI API"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": "Kullanıcı girdisine dayanarak, cümlenin ana konusunu veya amacını temsil eden bir arama kelimesi veya kelime öbeği çıkarın. Herhangi bir ek metin veya açıklama olmadan yalnızca arama sözcüğünü veya ifadesini çıktı olarak sağlayın."
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

def call_google_places_api(location: str, food_preference: Optional[str] = None) -> List[str]:
    """Call Google Places API and retrieve nearby places"""
    try:
        map_client = googlemaps.Client(MAPS_API_KEY)
        search_string = food_preference
        address = location
        geocode = map_client.geocode(address=address)
        (lat, lng) = map(geocode[0]['geometry']['location'].get, ('lat', 'lng'))

        response = map_client.places_nearby(
            location=(lat, lng),
            keyword=search_string,
            radius=1000
        )

        business_list = response.get('results')
        df = pd.DataFrame(business_list)
        df['url'] = 'https://www.google.com/maps/place/?q=place_id:' + df['place_id']

        top_places = df[(df['user_ratings_total'] > 100) & (df['rating'] >= 4.2)].sort_values(
            by=['rating', 'user_ratings_total'], ascending=False).head(4)

        places = []
        for _, place in top_places.iterrows():
            place_id = place['place_id']
            place_details = get_place_details(place_id, MAPS_API_KEY)
            if place_details:
                place_name = place_details.get("name", "N/A")
                place_rating = place_details.get("rating", "N/A")
                total_ratings = place_details.get("user_ratings_total", "N/A")
                place_address = place_details.get("vicinity", "N/A")
                place_url = place_details.get("url", "N/A")
                place_reviews = []

                reviews = place_details.get("reviews", [])
                for review in reviews[:5]:
                    review_dict = {"text": review["text"]}
                    place_reviews.append(review_dict)

                if ',' in place_address:
                    street_address = place_address.split(',')[0]
                else:
                    street_address = place_address

                place_info = f"[{place_name}]({place_url}) is a located at {street_address}. It has a rating of {place_rating} based on {total_ratings} user reviews: {place_reviews}. \n"
                places.append(place_info)

        return places
    except Exception as e:
        print(f"Error during the Google Places API call with radius 1000: {e}")
        try:
            response = map_client.places_nearby(
                location=(lat, lng),
                keyword=search_string,
                radius=2000
            )

            business_list = response.get('results')
            df = pd.DataFrame(business_list)
            df['url'] = 'https://www.google.com/maps/place/?q=place_id:' + df['place_id']

            top_places = df[(df['user_ratings_total'] > 100) & (df['rating'] >= 4.2)].sort_values(
                by=['rating', 'user_ratings_total'], ascending=False).head(4)

            places = []
            for _, place in top_places.iterrows():
                place_id = place['place_id']
                place_details = get_place_details(place_id, MAPS_API_KEY)
                if place_details:
                    place_name = place_details.get("name", "N/A")
                    place_rating = place_details.get("rating", "N/A")
                    total_ratings = place_details.get("user_ratings_total", "N/A")
                    place_address = place_details.get("vicinity", "N/A")
                    place_url = place_details.get("url", "N/A")
                    place_reviews = []

                    reviews = place_details.get("reviews", [])
                    for review in reviews[:5]:
                        review_dict = {"text": review["text"]}
                        place_reviews.append(review_dict)

                    if ',' in place_address:
                        street_address = place_address.split(',')[0]
                    else:
                        street_address = place_address

                    place_info = f"[{place_name}]({place_url}) is a located at {street_address}. It has a rating of {place_rating} based on {total_ratings} user reviews: {place_reviews}. \n"
                    places.append(place_info)

            return places
        except Exception as e:
            print(f"Error during the Google Places API call with radius 2000: {e}")
            return []

def provide_user_specific_recommendations(user_input: str, location: str) -> str:
    """Provide user-specific recommendations based on input and location"""
    place_type = generate_short_answer(user_input)
    places = call_google_places_api(location, place_type)
    if places:
        return f"Here are some places you might be interested in: {' '.join(places)}"
    else:
        return "Yakınlarda ilgi çekici bir yer bulamadım. Lütfen başka bir şekilde dile getirmeyi deneyiniz"

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """API endpoint for place recommendations"""
    data = request.json
    user_input = data.get('message')
    location = data.get('location')

    if not location:
        return jsonify({'error': 'Lütfen konum giriniz.'}), 400

    if not user_input:
        return jsonify({'error': 'Lütfen bir mesaj giriniz.'}), 400

    try:
        # Get place recommendations
        output = provide_user_specific_recommendations(user_input, location)

        # Generate AI response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "Sen bir mekan tavsiyecisisin. Kullanicinin sorusuna uygun mekanlari buluyorsun, mekan yorumlarini anlayarak o mekanlari neden secmesi gerektigini tek tek ozetliyorsun.**[cafe ismi](url link)** formatini muhakkak ver. Emoji kullanmaktan cekinme"
                },
                {
                    "role": "user",
                    "content": user_input + output
                }
            ],
            temperature=0,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        ai_response = response.choices[0].message.content
        return jsonify({'response': ai_response})

    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        return jsonify({'error': 'Bir hata oluştu. Lütfen tekrar deneyiniz.'}), 500

@app.route('/api/recommend/stream', methods=['POST'])
def recommend_stream():
    """API endpoint for streaming place recommendations"""
    data = request.json
    user_input = data.get('message')
    location = data.get('location')

    if not location:
        return jsonify({'error': 'Lütfen konum giriniz.'}), 400

    if not user_input:
        return jsonify({'error': 'Lütfen bir mesaj giriniz.'}), 400

    def generate():
        try:
            output = provide_user_specific_recommendations(user_input, location)

            stream = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir mekan tavsiyecisisin. Kullanicinin sorusuna uygun mekanlari buluyorsun, mekan yorumlarini anlayarak o mekanlari neden secmesi gerektigini tek tek ozetliyorsun.**[cafe ismi](url link)** formatini muhakkak ver. Emoji kullanmaktan cekinme"
                    },
                    {
                        "role": "user",
                        "content": user_input + output
                    }
                ],
                temperature=0,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
