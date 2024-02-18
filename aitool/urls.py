from django.urls import path
from .views import register, reg_success, login_user,handle_login_page,otp_verification,page,courses,home,askques

app_name = 'aitool'

urlpatterns = [
    path('reg/', register, name='register'),
    path('reg-success/<str:success_type>/<str:username>/', reg_success, name='reg_success'),
    path('login/', login_user, name='login'),
     path('login-page/', handle_login_page, name='login_page'),
     #path('send-otp-email/', send_otp_email, name='send_otp_email'),
     path('otp-verification/', otp_verification, name='otp_verification'),
     path('chat/', page , name = 'chat'),
    path('courses/',courses, name = 'courses'),
    path('home/<str:username>/',home, name = 'home'),
    path('ask_qns_from_pdf/',askques, name = 'ask_qns_from_pdf' ),

]
