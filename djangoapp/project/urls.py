from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from authentication.viewsets.viewsSetLogin import GoogleLoginView, GoogleRegisterView, CustomTokenObtainPairView
from authentication.viewsets.viewSetUsers import UserDetailView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from utils.common import generate_csrf_token
from email_service.views import CustomPasswordResetView
from .views import test_view

""" Rotas """
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from authentication.urls import router as authentication_router
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.tokens import RefreshToken

# Roteador principal v1
main_router_v1 = DefaultRouter()
# Inclua os roteadores de `Users` 
main_router_v1.registry.extend(authentication_router.registry)

# Lista de URLs de autenticação
auth_urls = [
    #AUTH JWT
    path('api/v1/auth/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/check/', TokenVerifyView.as_view(), name='token_check'), 
    path('api/v1/auth/user-detail/', UserDetailView.as_view(), name='user-detail'),
    path('api/v1/csrf-token/', generate_csrf_token, name='generate-csrf-token'),
    
    # Password reset URLs
    path('api/v1/auth/password-reset/send-email/', CustomPasswordResetView.as_view(), name='password_reset'),
    
    
    
    # Login Google
    path('api/v1/google-register/', GoogleRegisterView.as_view(), name='google-register'),
    path('api/v1/google-login/', GoogleLoginView.as_view(), name='google-login'),
]


urlpatterns = [
    path('admin/', admin.site.urls),  # URLs do Django admin

    *auth_urls,
        
    #AUTH ADMIN 
    path('auth/', include('rest_framework.urls')),   
    
    
    #API VERSÃO 1 V1 
    path('api/v1/', include(main_router_v1.urls)),

    #testes 
    path('test/', test_view, name='test_view'),


]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
