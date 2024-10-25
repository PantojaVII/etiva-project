from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from authentication.viewsets.viewsSetLogin import GoogleLoginView, GoogleRegisterView, CustomTokenObtainPairView
from authentication.viewsets.viewSetUsers import UserDetailView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from utils.common import generate_csrf_token
from email_service.views import CustomPasswordResetAPIView
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


API_VERSION = 'v1'

# Lista de URLs de autenticação
auth_urls = [
    #AUTH JWT
    path(f'api/{API_VERSION}/auth/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(f'api/{API_VERSION}/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(f'api/{API_VERSION}/auth/check/', TokenVerifyView.as_view(), name='token_check'), 
    path(f'api/{API_VERSION}/auth/user-detail/', UserDetailView.as_view(), name='user-detail'),
    path(f'api/{API_VERSION}/csrf-token/', generate_csrf_token, name='generate-csrf-token'),
    
    path(f'api/{API_VERSION}/auth/password-reset/send-email/', CustomPasswordResetAPIView.as_view(), name='password_reset'),# Password reset URLs
    path(f'api/{API_VERSION}/', include('payments.urls')),    # Pagamentos
    
    # Login Google
    path(f'api/{API_VERSION}/google-register/', GoogleRegisterView.as_view(), name='google-register'),
    path(f'api/{API_VERSION}/google-login/', GoogleLoginView.as_view(), name='google-login'),
]

urlpatterns = [
    path('admin/', admin.site.urls),  # URLs do Django admin

    *auth_urls,
    
    path('auth/', include('rest_framework.urls')),       #AUTH ADMIN 
    path(f'api/{API_VERSION}/', include(main_router_v1.urls)),    #API VERSÃO 1 

    # Soluções em IA
    path(f'api/{API_VERSION}/ai/creatus_cortex/', include('creatus_cortex.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
