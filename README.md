# PlaceRecommender

PlaceRecommender is an AI-powered chatbot that provides personalized place recommendations based on user preferences and location. It utilizes the OpenAI API for natural language processing and the Google Places API to fetch relevant place information.

## Demo

Check out the live demo of PlaceRecommender on Hugging Face Spaces: [PlaceRecommender Demo](https://huggingface.co/spaces/burak/PlaceRecommender)

## Features

- **Modern Web Interface**: Beautiful, responsive design with gradient backgrounds and smooth animations
- **Conversational AI**: Natural language processing powered by OpenAI GPT-3.5
- **Personalized Recommendations**: Tailored place suggestions based on your preferences and location
- **Real-time Integration**: Google Places API for accurate and up-to-date information
- **Smart Filtering**: Automatically filters places by rating (≥4.2) and review count (>100)
- **Rich Information**: Includes place names, addresses, ratings, and user reviews
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Two Interfaces**: Choose between modern web app or Gradio interface
- **RESTful API**: Backend API for easy integration with other applications

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/PlaceRecommender.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the necessary API keys:
   - OpenAI API Key: Set the `OPENAI_API_KEY` environment variable with your OpenAI API key.
   - Google Maps API Key: Set the `MAPS_API_KEY` environment variable with your Google Maps API key.

## Usage

### Option 1: Web Application (Recommended)

1. Run the Flask web application:
   ```
   python web_app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Enter your location in the designated input field (e.g., "Kadıköy, Moda").

4. Start interacting with the chatbot by asking for place recommendations based on your preferences.

5. The chatbot will provide personalized recommendations along with relevant details such as place name, address, rating, and user reviews.

### Option 2: Gradio Interface

1. Run the Gradio application:
   ```
   python app.py
   ```

2. Access the application through the provided URL in your web browser.

3. Enter your location in the designated input field.

4. Start interacting with the chatbot by asking for place recommendations based on your preferences.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Project Structure

```
PlaceRecommender/
├── web_app.py              # Flask web application (main web server)
├── app.py                  # Gradio interface (alternative UI)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main web page template
├── static/
│   ├── css/
│   │   └── style.css      # Styling for web interface
│   └── js/
│       └── app.js         # Frontend JavaScript logic
└── README.md
```

## API Endpoints

### POST /api/recommend
Get place recommendations based on user input and location.

**Request Body:**
```json
{
  "message": "Arkadaşlarımla oturup kahve içebileceğimiz bir yer arıyoruz",
  "location": "Kadıköy, Moda"
}
```

**Response:**
```json
{
  "response": "AI-generated recommendations with place details..."
}
```

### POST /api/recommend/stream
Stream place recommendations in real-time (Server-Sent Events).

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Model**: OpenAI GPT-3.5 Turbo
- **Maps API**: Google Places API & Google Maps API
- **Alternative UI**: Gradio
- **Data Processing**: Pandas
- **HTTP Client**: Requests

## Acknowledgements

- [OpenAI](https://openai.com/) for providing the powerful language model API.
- [Google Places API](https://developers.google.com/places/web-service/overview) for enabling access to accurate place information.
- [Gradio](https://gradio.app/) for the user-friendly interface components.
- [Flask](https://flask.palletsprojects.com/) for the lightweight web framework.

## Contact

For any inquiries or feedback, please contact the project maintainer:

Burak Kaya
- Email: burak.k3574@gmail.com
