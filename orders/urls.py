from django.urls import path
from orders.views import confirm_payment,create_order,list_orders,retrieve_order,update_order,delete_order

urlpatterns=[
    path('pay/<uuid:order_id>/', confirm_payment),
    path("orders/create/", create_order, name="create-order"),
    path("orders/", list_orders),
    path("orders/<uuid:order_id>/", retrieve_order),
    path("orders/<uuid:order_id>/update/", update_order),
    path("orders/<uuid:order_id>/delete/", delete_order),
]