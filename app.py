Here are the comments added to the code:

""" PlaceRecommender
@author: Burak Kaya
@email: burak.k3574@gmail.com

"""

import gradio as gr
from huggingface_hub import InferenceClient
import json
from openai import OpenAI
import os
import requests
import googlemaps
import pandas as pd

# Set API keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MAPS_API_KEY = os.environ.get('MAPS_API_KEY')

# Define error message for missing location input
LOC_ERR_MSG = "Lütfen yukaradıki bölümden konum giriniz."

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to get place details using Google Places API
def get_place_details(place_id, api_key):
    URL = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
    response = requests.get(URL)
    if response.status_code == 200:
        result = json.loads(response.content)["result"]
        return result
    else:
        print(f"Google Place Details API request failed with status code {response.status_code}")
        print(f"Response content: {response.content}")
        return None

# Function to generate a short answer using OpenAI API
def generate_short_answer(user_input):
    OpenAI(api_key=OPENAI_API_KEY)

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

    output_string = response.choices[0].message.content
    return output_string

# Function to call Google Places API and retrieve nearby places
def call_google_places_api(location, food_preference=None):
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

        top_places = df[(df['user_ratings_total'] > 100) & (df['rating'] >= 4.2)].sort_values(by=['rating', 'user_ratings_total']).sort_values(by=['rating','user_ratings_total'],ascending=False).head(4)

        places = []
        for _, place in top_places.iterrows():
            place_id = place['place_id']
            place_details = get_place_details(place_id, MAPS_API_KEY)            
            place_name = place_details.get("name", "N/A")
            place_rating = place_details.get("rating", "N/A")
            total_ratings = place_details.get("user_ratings_total", "N/A")
            place_address = place_details.get("vicinity", "N/A")
            place_url = place_details.get("url", "N/A")
            place_reviews = []

            reviews = place_details.get("reviews", [])
            for review in reviews[:5]:
              review_dict = {
                "text": review["text"],
            }
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

            top_places = df[(df['user_ratings_total'] > 100) & (df['rating'] >= 4.2)].sort_values(by=['rating', 'user_ratings_total']).sort_values(by=['rating','user_ratings_total'],ascending=False).head(4)

            places = []
            for _, place in top_places.iterrows():
                place_id = place['place_id']
                place_details = get_place_details(place_id, MAPS_API_KEY)            
                place_name = place_details.get("name", "N/A")
                place_rating = place_details.get("rating", "N/A")
                total_ratings = place_details.get("user_ratings_total", "N/A")
                place_address = place_details.get("vicinity", "N/A")
                place_url = place_details.get("url", "N/A")
                place_reviews = []

                reviews = place_details.get("reviews", [])
                for review in reviews[:5]:
                  review_dict = {
                    "text": review["text"],
                }
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

# Function to provide user-specific recommendations based on input and location
def provide_user_specific_recommendations(user_input, location):
    place_type = generate_short_answer(user_input)
    places = call_google_places_api(location, place_type)
    if places:
        return f"Here are some places you might be interested in: {' '.join(places)}"
    else:
        return "Yakınlarda ilgi çekici bir yer bulamadım. Lütfen başka bir şekilde dile getirmeyi deneyiniz"

# Main bot function to handle user input and generate responses
def bot(user_input, history,Konum):

    if not Konum:
        yield LOC_ERR_MSG

    if Konum:
        output = provide_user_specific_recommendations(user_input, Konum)

        OpenAI(api_key=OPENAI_API_KEY)


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
        #streaming
        partial_message = ""
        for chunk in stream:
          if chunk.choices[0].delta.content is not None:
            partial_message = partial_message + chunk.choices[0].delta.content
            yield partial_message

        yield partial_message

# Set the theme for the Gradio interface
my_theme = gr.Theme.from_hub("bethecloud/storj_theme")

# Create the Gradio interface
with gr.Blocks(theme = my_theme) as demo:
    #gr.HTML("<h1><center>MÜDAVİM<h1><center>")
    with gr.Row() as Konum:
        Konum = gr.Textbox(label="Konum",placeholder="Konum Giriniz (Kadıköy, Moda)")

    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        render=False,
        height=500,
    )


    gr.ChatInterface(
        bot,chatbot=chatbot,
          additional_inputs=Konum,
            examples=[["Arkadașlarımla oturup kahve içebileceğimiz bir yer arıyoruz. Önerebileceğin yerler var mı?"], ["Bilgisayar ile çalışabileceğim sessiz kafe var mı?"], ["Kız arkadaşım ile özel bir akşam yemeği yemek istiyoruz. Bir tavsiyen var mı?"]],)

# Run the Gradio interface
if __name__ == "__main__":
    demo.launch(show_api=False)