import os
import sys
import django

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant_recommender.settings")
django.setup()

from restaurants.models import Restaurant  # Import after setup!
from openai import OpenAI
import json

# Ensure your API key is loaded
client = OpenAI()

# Function to generate embeddings for all restaurants
def generate_embeddings():
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        text_data = (
            f"{restaurant.name} {restaurant.neighborhood} "
            f"{restaurant.cuisine_general} {restaurant.cuisine_specific} "
            f"{restaurant.vibe} {restaurant.occasions} "
            f"{restaurant.type_of_meal} {restaurant.dietary_restrictions}"
        )

        # Generate OpenAI embedding
        response = client.embeddings.create(input=text_data, model="text-embedding-3-small")
        embedding = response.data[0].embedding

        # Save embedding
        restaurant.embedding = json.dumps(embedding)  # Convert list to JSON string
        restaurant.save()
        print(f"✅ Saved embedding for: {restaurant.name}")

# Run the function
if __name__ == "__main__":
    generate_embeddings()
