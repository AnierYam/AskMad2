import pandas as pd
from django.core.management.base import BaseCommand
from restaurants.models import Restaurant

class Command(BaseCommand):
    help = 'Import restaurants from an Excel file'

    def handle(self, *args, **kwargs):
        file_path = 'restaurants/data/restaurants.xlsx'  # Update if needed

        try:
            df = pd.read_excel(file_path, engine='openpyxl')

            for _, row in df.iterrows():
                Restaurant.objects.create(
                    name=row['Name'],
                    address=row['Address'],
                    instagram=row.get('Instagram', ''),
                    neighborhood=row['Neighborhood'],
                    area=row['Area'],
                    cuisine_specific=row['Cuisine Specific'],
                    cuisine_general=row['Cuisine General'],
                    opening_hours=row['Opening Days/ Hours'],
                    vibe=row['Vibe'],
                    occasions=row['Occasions'],
                    type_of_meal=row['Type of meal'],
                    dietary_restrictions=row.get('Dietary restrictions', ''),
                    reservation_link=row.get('Reservation Link', ''),
                    directions_link=row.get('Directions Link', '')  # ✅ Add this line
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(df)} restaurants!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
