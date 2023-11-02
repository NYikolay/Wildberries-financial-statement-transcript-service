from django.urls import path, re_path

from users.views import (
    LoginPageView, LogoutView, RegisterPageView,
    LoadDataFromWBView,
    ChangePasswordView, CompaniesListView, CompanyEditView,
    EditProductView, ProductDetailView, EmptyProductsListView,
    DeleteCompanyView, ConfirmRegistrationView, ConfirmEmailPageView, PasswordResetView, PasswordResetConfirmView,
    PasswordResetDoneView, CheckReportsLoadingStatus, SetNetCostsFromFileView, ExportNetCostsExampleView,
    ProfileSubscriptionsPage, CreateApiKeyView, UpdateApiKeyView
)

app_name = 'users'

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(
        'password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'
    ),

    path('register/', RegisterPageView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/',
         ConfirmRegistrationView.as_view(), name='activate_email'),
    path('email/confirmation/', ConfirmEmailPageView.as_view(), name='email_confirmation_info'),

    path('profile/subscriptions/', ProfileSubscriptionsPage.as_view(), name='profile_subscriptions'),
    path('create-api-key/', CreateApiKeyView.as_view(), name='create_api_key'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/companies/', CompaniesListView.as_view(), name='companies_list'),
    path('profile/api-key/edit/<int:api_key_id>/', UpdateApiKeyView.as_view(), name='api_key_edit'),
    path('profile/company/delete/<int:api_key_id>/', DeleteCompanyView.as_view(), name='company_delete'),

    path('product/<int:article_value>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/edit/<int:article_value>/', EditProductView.as_view(), name='edit_product'),
    path('products/', EmptyProductsListView.as_view(), name='empty_products'),
    path('set-net-costs/', SetNetCostsFromFileView.as_view(), name='set_net_costs'),
    path('export-net-costs-example/', ExportNetCostsExampleView.as_view(), name='export_net_costs_example'),

    path('send-request-for-report/', LoadDataFromWBView.as_view(), name='send_request_for_report'),
    path('sheck-reports-loading-status/', CheckReportsLoadingStatus.as_view(), name='check_reports_loading_status'),
]
