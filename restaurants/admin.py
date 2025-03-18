from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from import_export.formats.base_formats import XLSX  # ✅ Enables Excel support
from .models import Restaurant  # ✅ Ensure this model exists

# ✅ Step 1: Define a Resource Class for Import/Export
class RestaurantResource(ModelResource):
    class Meta:
        model = Restaurant  # ✅ Automatically includes ALL fields from the model
        import_id_fields = ('name',)  # 🔎 Ensures uniqueness based on name + id
        skip_unchanged = True  # ✅ Skips unchanged rows
        report_skipped = True  # ✅ Shows skipped rows in admin

    def get_instance(self, instance_loader, row):
        """ Updates existing restaurants instead of creating duplicates. """
        return Restaurant.objects.filter(name=row.get("name"), id=row.get("id")).first()

    def before_import_row(self, row, **kwargs):
        """ Ensures updates instead of duplication. """
        if Restaurant.objects.filter(name=row.get("name"), id=row.get("id")).exists():
            return  # Skip creation, update instead

# ✅ Step 2: Merge Admin Features (Manual Entry + Import/Export)
@admin.register(Restaurant)
class RestaurantAdmin(ImportExportModelAdmin):  # ✅ Combines manual entry + import/export
    resource_class = RestaurantResource  # ✅ Links to the import-export configuration
    formats = [XLSX]  # ✅ Enables Excel support

    list_display = (
        'name', 'address', 'neighborhood', 'area', 'cuisine_general', 'cuisine_specific',
        'opening_hours', 'vibe', 'occasions', 'type_of_meal', 'dietary_restrictions',
        'instagram', 'reservation_link', 'directions_link'  # ✅ Includes all fields in the table view
    )  

    search_fields = (
        'name', 'address', 'neighborhood', 'area', 'cuisine_general', 'cuisine_specific',
        'opening_hours', 'vibe', 'occasions', 'type_of_meal', 'dietary_restrictions',
        'instagram', 'reservation_link', 'directions_link'  # ✅ Now all fields are searchable!
    )  

    list_filter = ('neighborhood', 'area', 'cuisine_general', 'cuisine_specific')  # ✅ Optional: Adds filters in the admin panel for quick selection
