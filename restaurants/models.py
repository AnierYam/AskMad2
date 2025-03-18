from dotenv import load_dotenv
load_dotenv()

from django.db import models
from openai import OpenAI
import os

# ✅ Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    cuisine_general = models.TextField(blank=True, null=True)
    cuisine_specific = models.TextField(blank=True, null=True)
    opening_hours = models.TextField(blank=True, null=True)  # ✅ "Opening Days/ Hours" from Excel
    vibe = models.TextField(blank=True, null=True)
    occasions = models.TextField(blank=True, null=True)
    type_of_meal = models.TextField(blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    reservation_link = models.URLField(blank=True, null=True)
    directions_link = models.URLField(blank=True, null=True)  # ✅ NEW FIELD ADDED

    # ✅ New field to store the embedding
    embedding = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def generate_embedding(self):
        """
        Generates an embedding for this restaurant's attributes using OpenAI.
        The text includes all key fields from your Excel table.
        """
        text = (
            f"Name: {self.name}. "
            f"Address: {self.address}. "
            f"Neighborhood: {self.neighborhood}. "
            f"Area: {self.area}. "
            f"Cuisine General: {self.cuisine_general}. "
            f"Cuisine Specific: {self.cuisine_specific}. "
            f"Opening Hours: {self.opening_hours}. "
            f"Vibe: {self.vibe}. "
            f"Occasions: {self.occasions}. "
            f"Type of Meal: {self.type_of_meal}. "
            f"Dietary Restrictions: {self.dietary_restrictions}."
        )
        response = client.embeddings.create(
            model="text-embedding-3-small",  # ✅ Ensuring consistent embedding model
            input=text
        )
        return response.data[0].embedding  # ✅ Extracts the embedding vector

    def save(self, *args, **kwargs):
        """
        Automatically generate an embedding when a restaurant is created or updated,
        but only if it hasn't been created already.
        """
        if not self.embedding:
            self.embedding = self.generate_embedding()
        super().save(*args, **kwargs)
