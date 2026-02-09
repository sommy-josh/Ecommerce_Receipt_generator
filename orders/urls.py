from django.urls import path
from orders.views import confirm_payment

urlpatterns=[
    path('pay/<uuid:order_id>/', confirm_payment),
]