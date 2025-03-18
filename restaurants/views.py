from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import traceback
from openai import OpenAI
from dotenv import load_dotenv
from django.db.models import Q
from .models import Restaurant

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

### ✅ Helper: Fetch All Restaurants (NO FILTERING)
def get_all_restaurants():
    """Fetch all restaurants without filtering."""
    all_restaurants = Restaurant.objects.all()

    restaurants_data = [
        {
            "id": r.id,
            "name": r.name,
            "neighborhood": r.neighborhood,
            "cuisine": r.cuisine_specific,
            "general_cuisine": r.cuisine_general,
            "vibe": r.vibe,
            "dietary_restrictions": r.dietary_restrictions,
            "meal_type": r.type_of_meal,
            "occasions": r.occasions,
            "instagram": r.instagram,  
            "reservation_link": r.reservation_link,  
            "directions_link": r.directions_link,  
        }
        for r in all_restaurants
    ]
    return restaurants_data

### ✅ Helper: Ask GPT for Recommendations (1 Main Pick + 2 Additional)
def ask_gpt_for_recommendations(user_query, restaurants_data):
    """Send restaurant data to GPT and ask it to select the best matches."""

    system_prompt = """
    You are Mady, an upbeat and knowledgeable food-loving assistant helping users find the best restaurant match!
    
    Your job is to analyze the restaurant database and select:
    - **1 Main Pick** (BEST match)
    - **2 Additional Suggestions** (also great, but slightly less ideal)
    
    Consider:
    - Cuisine match (if specified)
    - Dietary restrictions (if specified)
    - Vibe (casual, fancy, cozy, trendy, romantic, etc.)
    - Meal Type (brunch, dinner, coffee, etc.)
    - Occasion (date night, business lunch, family gathering, etc.)
    - Time relevance (e.g., open late, breakfast spot)
    - Favoring spots with Instagram & reservations (if applicable)

    🎯 **TONE:** Be lively, fun, and conversational in the descriptions!

    **Output Structure (JSON Format):**
    {
        "main_pick": {
            "id": 123,
            "name": "Best Restaurant",
            "neighborhood": "Fairfax",
            "reason": "A lively Italian gem in Fairfax with perfect date-night vibes!",
            "instagram": "https://instagram.com/restaurant",
            "reservation_link": "https://opentable.com/reserve",
            "directions_link": "https://maps.google.com/?q=restaurant"
        },
        "additional_suggestions": [
            {
                "id": 456,
                "name": "Great Backup",
                "neighborhood": "Georgetown",
                "reason": "A cozy sushi spot with killer ambiance and sake flights.",
                "instagram": "https://instagram.com/sushi",
                "reservation_link": "https://opentable.com/sushi",
                "directions_link": "https://maps.google.com/?q=sushi"
            },
            {
                "id": 789,
                "name": "Another Solid Choice",
                "neighborhood": "Dupont Circle",
                "reason": "Trendy all-day café with organic options and a sunny patio!",
                "instagram": "https://instagram.com/cafe",
                "reservation_link": "https://opentable.com/cafe",
                "directions_link": "https://maps.google.com/?q=cafe"
            }
        ]
    }
    """

    user_message = f"""
    User query: {user_query}

    Restaurant database:
    {json.dumps(restaurants_data, indent=2)}

    Select **1 main pick** and **2 additional suggestions** and return them in the expected format.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            response_format={"type": "json_object"} 
        )

        response_content = response.choices[0].message.content
        print(f"GPT Response: {response_content}")

        try:
            parsed_response = json.loads(response_content)

            if "main_pick" in parsed_response and "additional_suggestions" in parsed_response:
                return parsed_response
            
            print("⚠️ Unexpected response structure from GPT")
            return {}

        except json.JSONDecodeError:
            print(f"❌ Error parsing JSON response: {response_content}")
            return {}

    except Exception as e:
        print(f"❌ Error calling OpenAI API: {str(e)}")
        return {}

### 🔹 View: Render Restaurant Search Page
def restaurant_list_view(request):
    """Displays the restaurant search page."""
    return render(request, 'restaurants/restaurant_list.html')

### 🔹 View: Process Voice Query & Store Results
@csrf_exempt
def process_voice_request(request):
    """Process the user's request and trigger the overlay for loading."""

    print("✅ Received request to process voice query.")

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_query = data.get("query", "").strip()

            print(f"📝 User Query: {user_query}")

            if not user_query:
                return JsonResponse({"success": False, "error": "Empty query"}, status=400)

            # Step 1: Get all restaurants (NO FILTERING)
            restaurants_data = get_all_restaurants()
            print(f"📊 Total Restaurants Loaded: {len(restaurants_data)}")

            # Step 2: Ask GPT for recommendations
            gpt_results = ask_gpt_for_recommendations(user_query, restaurants_data)

            if not gpt_results:
                return JsonResponse({"success": False, "error": "No matches found"}, status=404)

            # Step 3: Store results in session
            request.session['search_result_main'] = gpt_results.get("main_pick", {})
            request.session['search_result_additional'] = gpt_results.get("additional_suggestions", [])
            request.session['user_query'] = user_query

            return JsonResponse({"success": True})  # ✅ No redirect, just signals overlay to stop

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

### 🔹 View: Render Search Results Page
def restaurant_results_view(request):
    """Displays the restaurant recommendations page based on stored session data."""
    try:
        user_query = request.session.get('user_query', '')

        if not user_query:
            return redirect("list")

        main_pick = request.session.get('search_result_main', {})
        additional_suggestions = request.session.get('search_result_additional', [])

        return render(request, 'restaurants/restaurant_results.html', {
            'main_pick': main_pick,
            'additional_suggestions': additional_suggestions,
            'user_query': user_query,
        })

    except Exception as e:
        print(f"❌ Error in restaurant_results_view: {str(e)}")
        print(traceback.format_exc())
        return render(request, 'restaurants/error.html', {
            'error_message': f"Error retrieving restaurant results: {str(e)}"
        })
