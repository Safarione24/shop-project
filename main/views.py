from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, F
from .models import Product, Category, Order, OrderItem, Review
from django.contrib.auth.models import User

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class HomeView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(is_deleted=False)
        category_id = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_deleted=False)
        return context

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

class MyLoginView(LoginView):
    template_name = 'login.html'
    next_page = reverse_lazy('home')

class MyLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'price', 'category', 'stock_quantity']
    template_name = 'product_form.html'
    success_url = reverse_lazy('home')

class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'price', 'category', 'stock_quantity']
    template_name = 'product_form.html'
    success_url = reverse_lazy('home')

class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(success_url)

class CreateOrderView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs['product_id'])
        if product.stock_quantity > 0:
            order = Order.objects.create(user=request.user, status='Новый')
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price_at_purchase=product.price
            )
            product.stock_quantity -= 1
            product.save()
        return redirect('order_history')

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_together().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class AdminUsersView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin_users.html'
    context_object_name = 'users_list'

class LeaveReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'comment']
    template_name = 'review_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = get_object_or_404(Product, id=self.kwargs['product_id'])
        return super().form_valid(form)

class SalesReportView(AdminRequiredMixin, TemplateView):
    template_name = 'sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        items = OrderItem.objects.all()
        if start_date and end_date:
            items = items.filter(order__created_at__range=[start_date, end_date])
        total_sales = items.aggregate(total=Sum(F('quantity') * F('price_at_purchase')))['total'] or 0
        context['total_sales'] = total_sales
        context['items'] = items
        return context
