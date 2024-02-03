from flask import Flask, render_template, request, jsonify
import openai
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pymongo import MongoClient
from datetime import datetime
import re
import config

import requests as req
app = Flask(__name__)
app = Flask("News_api")

# Set up OpenAI API credentials
openai.api_key = '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'

# Define some general questions
general_questions = [
    "Tell me about yourself.",
    "What is your favorite book?",
    "What is the capital of France?",
    "What are the benefits of exercise?",
]
# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    # Open and preprocess the image
    img = Image.open(image_path)

    # Enhance contrast and sharpness
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Adjust the enhancement factor as needed

    # Apply additional filters if necessary
    img = img.filter(ImageFilter.SMOOTH_MORE)

    return img

emissions_per_kilometer = {
    "bike": 0,
    "bicycle": 0,
    "car": 200,  # Example value in grams per kilometer
    "bus": 100,  # Example value in grams per kilometer
}
@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# @app.route('/knowledgequiz')
# def knowledgequiz():
#     return render_template('knowledgequiz.html')


# @app.route('/dailyquiz')
# def dasdailyquiz():
#     return render_template('dailyquiz.html')



@app.route('/streaks')
def streaks():
    return render_template('streaks.html')


@app.route('/events')
def events():
    return render_template('event.html')



@app.route('/eventform')
def eventform():
    return render_template('eventform.html')


@app.route('/sustainabilityquiz')
def sustainabilityquiz():
  
    return render_template('sus.html')


@app.route('/dailyquiz')
def dailyquiz():
    return render_template('dailyquiz.html')


@app.route('/ecommerce')
def ecommerce():
    return render_template('ecommerce.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/calculator')
def calculator():
    return render_template('calculator.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/offset')
def offset():
    return render_template('offset.html')

@app.route("/calculate_emissions", methods=["POST"])
def calculate_emissions():
    try:
        distance = float(request.form["distance"])
        transportation = request.form["transportation"]
        usual_transportation = request.form["usualTransportation"]
        fuel_type = request.form["fuelType"]
        mileage = float(request.form["mileage"])

        emissions = (distance / mileage) * emissions_per_kilometer[transportation]
        savings = (distance / mileage) * emissions_per_kilometer[usual_transportation] - emissions

        return jsonify({
            "carbon_emissions": round(emissions, 2),
            "savings": round(savings, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html", general_questions=general_questions)

@app.route("/api", methods=["POST"])
def api():
    message = request.json.get("message")
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    )
    
    response = completion.choices[0].message['content'] if completion.choices and completion.choices[0].message else 'Failed to Generate response!'
    
    return jsonify({"response": response})



@app.route("/ticketvalidation")
def ticketvalidation():
    return render_template("ticketvalidation.html")

@app.route("/upload_ticket", methods=["POST"])
def upload_ticket():
    image = request.files["ticket_image"]
    
    # Preprocess the image
    preprocessed_img = preprocess_image(image)
    
    # Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(preprocessed_img, lang='eng')
    
    destination_pattern = r'\b[^\d\s]+\s+To\s+[^\d\s]+\b'
    date_pattern = r'\d{2}/\d{2}/\d{4}'
    uts_pattern = r'UTS: (\d{8})'  # Updated UTS number pattern

    destination_matches = re.findall(destination_pattern, text)
    date_matches = re.findall(date_pattern, text)
    uts_matches = re.search(uts_pattern, text)

    if destination_matches or date_matches:
        destinations = [match.strip() for match in destination_matches]
        extracted_date_str = date_matches[0]
        
        extracted_date = datetime.strptime(extracted_date_str, '%d/%m/%Y').date()
        current_date = datetime.now().date()
        is_valid_ticket = current_date == extracted_date
        
        uts_number = uts_matches.group(1) if uts_matches else None  # Extract UTS number

        client = MongoClient("mongodb://localhost:27017/")
        db = client["codestrom"]
        collection = db["tickets"]

        document = {
            "destinations": destinations,
            "date": extracted_date_str,
            "is_valid_ticket": is_valid_ticket,
            "uts_number": uts_number
        }
        result = collection.insert_one(document)

        if is_valid_ticket:
            return jsonify({"message": "valid", "uts_number": uts_number})
        else:
            return jsonify({"message": "invalid"})
    else:
        return jsonify({"message": "Destinations or Date not found in the text"})
    











    


@app.route('/index')
def index():
    url = "https://newsapi.org/v2/top-headlines?country=in&pageSize=10&apiKey={}".format(
        config.API_KEY)
    Response = req.get(url)
    TopNews = Response.json()
    return render_template("index.html", News=TopNews)

@app.route('/business')
def business():
        url = "https://newsapi.org/v2/top-headlines?country=in&category=business&pageSize=10&apiKey={}".format(
        config.API_KEY)
        Response = req.get(url)
        TopNews = Response.json()
        return render_template("business.html", News=TopNews, num=len(TopNews['articles']))


@app.route('/entertainment')
def entertainment():
    url = "https://newsapi.org/v2/top-headlines?category=entertainment&pageSize=10&apiKey={}".format(
        config.API_KEY)
    Response = req.get(url)
    TopNews = Response.json()
    return render_template("entertainment.html", News=TopNews, num=len(TopNews['articles']))

@app.route('/general')
def general():
    url = "https://newsapi.org/v2/top-headlines?category=general&pageSize=10&apiKey={}".format(
        config.API_KEY)
    Response = req.get(url)
    TopNews = Response.json()
    return render_template("general.html", News=TopNews, num=len(TopNews['articles']))

@app.route('/health')
def health():
    url = "https://newsapi.org/v2/top-headlines?category=health&pageSize=10&apiKey={}".format(
        config.API_KEY)
    Response = req.get(url)
    TopNews = Response.json()
    return render_template("health.html", News=TopNews, num=len(TopNews['articles']))

@app.route('/science')
def science():
    url = "https://newsapi.org/v2/top-headlines?category=science&pageSize=10&apiKey={}".format(
        config.API_KEY)
    Response = req.get(url)
    TopNews = Response.json()
    return render_template("science.html", News=TopNews, num=len(TopNews['articles']))

@app.route('/technology')
def technology():
    url = "https://newsapi.org/v2/top-headlines?category=technology&pageSize=10&apiKey={}".format(
        config.API_KEY)
    Response = req.get(url)
    TopNews = Response.json()
    return render_template("technology.html", News=TopNews, num=len(TopNews['articles']))



if __name__ == '__main__':
    app.run(debug=True)
