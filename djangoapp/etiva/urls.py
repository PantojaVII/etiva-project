from django.urls import path
from .views import activity_list, participant_card, activity_detail

urlpatterns = [
    path('participants/<slug:slug>/card/', participant_card, name='participant_card'),  
    path('activity/<slug:slug>/', activity_detail, name='activity_detail'),  
    path('atividades/', activity_list, name='activity_list'),
    
]
