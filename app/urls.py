
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('financas/', include('financas.urls')),
    path('contas/', include('contas.urls')),
]

