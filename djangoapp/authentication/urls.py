from django.urls import path
from rest_framework import routers

from .viewsets.viewSetUsers import UserViewSet
from .viewsets.viewSetProfiles import ProfileViewSet
 
router = routers.DefaultRouter() 
router.register('users', UserViewSet)
router.register('profiles', ProfileViewSet)

 