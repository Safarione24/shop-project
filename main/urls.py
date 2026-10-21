from django.urls import path
from .views import (
    HomeView, RegisterView, MyLoginView, MyLogoutView,
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    CreateOrderView, OrderHistoryView, AdminUsersView, LeaveReviewView, SalesReportView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('product/add/', ProductCreateView.as_view(), name='product_add'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:product_id>/order/', CreateOrderView.as_view(), name='create_order'),
    path('orders/', OrderHistoryView.as_view(), name='order_history'),
    path('users/', AdminUsersView.as_view(), name='admin_users'),
    path('product/<int:product_id>/review/', LeaveReviewView.as_view(), name='leave_review'),
    path('report/', SalesReportView.as_view(), name='sales_report'),
]
