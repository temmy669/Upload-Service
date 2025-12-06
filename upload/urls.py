from django.urls import path
from .views import UploadView, UploadStatusView, UploadResultView

urlpatterns = [
    path("upload/", UploadView.as_view()),
    path("upload/<uuid:id>/status/", UploadStatusView.as_view()),
    path("upload/<uuid:id>/result/", UploadResultView.as_view()),
]
