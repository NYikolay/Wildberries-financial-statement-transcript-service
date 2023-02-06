from django.urls import path, re_path

from users.views import (
    LoginPageView, LogoutView, RegisterPageView,
    ProfilePage, LoadDataFromWBView, ChangeProfileData,
    ChangePasswordView, CompaniesListView, CompanyEditView,
    EditProductView, ProductDetailView, EmptyProductsListView,
    DeleteCompanyView, ara, ConfirmRegistrationView, ConfirmEmailPageView, PasswordResetView, PasswordResetConfirmView,
    PasswordResetDoneView
)

app_name = 'users'

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('ara/', ara, name='ara'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(
        'password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'
    ),

    path('register/', RegisterPageView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/',
         ConfirmRegistrationView.as_view(), name='activate_email'),
    path('email/confirmation/', ConfirmEmailPageView.as_view(), name='email_confirmation_info'),


    path('profile/', ProfilePage.as_view(), name='profile'),
    path('profile/companies/', CompaniesListView.as_view(), name='companies_list'),
    path('profile/company/edit/<int:api_key_id>/', CompanyEditView.as_view(), name='company_edit'),
    path('profile/company/delete/<int:api_key_id>/', DeleteCompanyView.as_view(), name='company_delete'),

    path('profile/product/<int:article_value>/', ProductDetailView.as_view(), name='product_detail'),
    path('profile/product/edit/<int:article_value>/', EditProductView.as_view(), name='edit_product'),
    path('products/', EmptyProductsListView.as_view(), name='empty_products'),

    path('send-request-for-report/', LoadDataFromWBView.as_view(), name='send_request_for_report'),

    path('change-user-profile/', ChangeProfileData.as_view(), name='change_user_profile'),
    path('change-user-password/', ChangePasswordView.as_view(), name='change_user_password'),
]
