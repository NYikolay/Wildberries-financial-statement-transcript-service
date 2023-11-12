from django.urls import path, re_path, include

from users.views import (
    LoginPageView, LogoutView, RegisterPageView,
    LoadDataFromWBView,
    ChangePasswordView, CompaniesListView, ProductDetailView,
    DeleteApiKeyView, ConfirmRegistrationView, ConfirmEmailPageView, PasswordResetView, PasswordResetConfirmView,
    PasswordResetDoneView, CheckReportsLoadingStatus, SetNetCostsFromFileView, ExportNetCostsExampleView,
    ProfileSubscriptionsPage, CreateApiKeyView, UpdateApiKeyView, ChangeCurrentApiKeyView, TaxRateListView,
    CreateTaxRateView, ChangeTaxRateView, DeleteTaxRateView, CostsListView, ChangeCostsView, CreateNetCostView,
    UpdateNetCostView, DeleteNetCostView, EmptyProductsView, ExecuteLoadingReportsFromWildberriesView, NotifySseUserView
)

import django_eventstream

app_name = 'users'

urlpatterns = [
    path('user/<user_id>/events/', include(django_eventstream.urls), {
        'format-channels': ['user-{user_id}']
    }),
    path('notify/user/', NotifySseUserView.as_view(), name='notify_user'),

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
    path('change-current-api-key/', ChangeCurrentApiKeyView.as_view(), name='change_current_api_key'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/companies/', CompaniesListView.as_view(), name='companies_list'),

    path('profile/taxes', TaxRateListView.as_view(), name='profile_taxes'),
    path('profile/taxes/change/<int:id>/', ChangeTaxRateView.as_view(), name='change_tax_rate'),
    path('profile/taxes/delete/<int:id>/', DeleteTaxRateView.as_view(), name='delete_tax_rate'),
    path('profile/taxes/create/', CreateTaxRateView.as_view(), name='create_tax_rate'),

    path('profile/costs/', CostsListView.as_view(), name='costs_list'),
    path('profile/costs/change/<str:create_dt>/', ChangeCostsView.as_view(), name='change_costs'),

    path('profile/api-key/edit/<int:api_key_id>/', UpdateApiKeyView.as_view(), name='api_key_edit'),
    path('profile/company/delete/<int:api_key_id>/', DeleteApiKeyView.as_view(), name='company_delete'),

    path('products/', EmptyProductsView.as_view(), name='empty_products'),
    path('product/<int:article>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/create/net-cost/', CreateNetCostView.as_view(), name='product_net_cost_create'),
    path('product/update/net-cost/<int:id>/', UpdateNetCostView.as_view(), name='product_net_cost_update'),
    path('product/delete/net-cost/<int:id>', DeleteNetCostView.as_view(), name='product_net_cost_delete'),

    path('set-net-costs/', SetNetCostsFromFileView.as_view(), name='set_net_costs'),
    path('export-net-costs-example/', ExportNetCostsExampleView.as_view(), name='export_net_costs_example'),

    # path('send-request-for-report/', LoadDataFromWBView.as_view(), name='send_request_for_report'),
    path('load-reports/', ExecuteLoadingReportsFromWildberriesView.as_view(), name='load_reports'),
    path('sheck-reports-loading-status/', CheckReportsLoadingStatus.as_view(), name='check_reports_loading_status'),
]
