from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_bi(request):
    return render(request, 'dashboards/dashboard_bi.html')
