from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from core import models
from doctor.mixins import UserIsDoctorMixin


class IndexView(UserIsDoctorMixin):

    # noinspection PyMethodMayBeStatic
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return render(request, 'doctor/no-associated-shelter.html')


class SummaryView(UserIsDoctorMixin, TemplateView):
    template_name = 'doctor/summary.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['active_menu_item'] = 'summary'

        # noinspection PyUnresolvedReferences
        doctor = models.Doctor.get_doctor_by_user(self.request.user)
        patient = doctor.get_patient()

        reports = models.DailyIntakesReport.filter_for_user(
            patient.patient_user).annotate_with_nutrient_totals(). \
            exclude_empty_intakes(). \
            order_by('-date')

        context['nutrition_reports'] = reports
        context['patient_profile'] = patient.patient_user.profile

        return context


class NutritionView(UserIsDoctorMixin, ListView):
    template_name = 'doctor/nutrition.html'
    context_object_name = 'reports'
    model = models.DailyIntakesReport
    paginate_by = 30

    def get_queryset(self):
        # noinspection PyUnresolvedReferences
        doctor = models.Doctor.get_doctor_by_user(self.request.user)
        patient = doctor.get_patient()

        reports = models.DailyIntakesReport.filter_for_user(
            patient.patient_user).annotate_with_nutrient_totals(). \
            prefetch_intakes(). \
            exclude_empty_intakes(). \
            order_by('-date')

        return reports

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'nutrition'

        return context


class HealthStatusView(UserIsDoctorMixin, ListView):
    template_name = 'doctor/health-status.html'
    context_object_name = 'statuses'
    model = models.DailyHealthStatus
    paginate_by = 30

    def get_queryset(self):
        # noinspection PyUnresolvedReferences
        doctor = models.Doctor.get_doctor_by_user(self.request.user)
        patient = doctor.get_patient()

        statuses = models.DailyHealthStatus.filter_for_user(patient.patient_user) \
            .prefetch_all_related_fields() \
            .order_by('-date')

        return statuses

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'health_status'

        return context


class AutomaticDialysisView(UserIsDoctorMixin, ListView):
    template_name = 'doctor/automatic-dialysis.html'
    context_object_name = 'dialyses'
    model = models.AutomaticPeritonealDialysis
    paginate_by = 30

    def get_queryset(self):
        # noinspection PyUnresolvedReferences
        doctor = models.Doctor.get_doctor_by_user(self.request.user)
        patient = doctor.get_patient()

        statuses = models.AutomaticPeritonealDialysis.filter_for_user(patient.patient_user) \
            .prefetch_all_related() \
            .order_by('-started_at')

        return statuses

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_menu_item'] = 'automatic_dialysis'

        return context


@login_required(redirect_field_name=None)
def no_associated_shelter(request: HttpRequest) -> HttpResponse:
    return render(request, 'doctor/no-associated-shelter.html')
