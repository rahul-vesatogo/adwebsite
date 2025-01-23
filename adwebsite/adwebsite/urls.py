from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView 
from adwebsite.schema import schema
from adwebsite.views import login_page, home, custom_logout
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path('accounts/', include("django.contrib.auth.urls")),
    path('login/', login_page, name='login_page'),
    path('home/', home, name="home"),
    path('logout/', custom_logout, name="logout")

]
