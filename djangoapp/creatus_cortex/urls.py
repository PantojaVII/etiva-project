from django.urls import path
from .views import GenerateImageView, ListGeneratedImagesView, DeleteImagesView

urlpatterns = [
    path('generate/', GenerateImageView, name='generate_image'),
    path('list-images-creatus/', ListGeneratedImagesView, name='list_images'),
    path('delete-image/', DeleteImagesView, name='delete-images'),
]
