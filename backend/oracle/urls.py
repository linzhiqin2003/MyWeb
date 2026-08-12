from django.urls import path
from .views import DailyOracleView, DivinationView

urlpatterns = [
    path("divine/", DivinationView.as_view(), name="divine"),
    path("daily/", DailyOracleView.as_view(), name="tarot-daily"),
]
