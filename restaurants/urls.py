from django.urls import path
from .views import (
    restaurant_list_view,
    process_voice_request,
    restaurant_results_view
)

urlpatterns = [
    path('', restaurant_list_view, name='list'),  # ✅ Homepage for /restaurants/
    path('process-voice/', process_voice_request, name='voice'),  # ✅ Processes user query
    path('results/', restaurant_results_view, name='results'),  # ✅ Shows restaurant results
]
