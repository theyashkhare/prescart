from django.contrib import admin
import products.urls
import orders.urls
from orders.views import TransactionAPIView
from django.urls import path, include
from payments.views import init_payment
import carts.urls
import accounts.urls
import marketing.urls
import payments.urls
from django.conf import settings
from django.conf.urls.static import static


api_urlpatterns = [
    path('products/', include(products.urls.api_urlpatterns)),
    path('orders/', include(orders.urls.api_urlpatterns)),
    path('cart/', include(carts.urls.api_urlpatterns)),
    path('marketing/', include(marketing.urls)),
    path('payment/', include(payments.urls))
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(accounts.urls)),
    path('api/', include(api_urlpatterns)),
    path('keys/', TransactionAPIView.as_view(), name="transaction_api")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
