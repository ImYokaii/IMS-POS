import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from pos_view.models import SalesInvoice, SalesInvoiceItem
from procurement_view.models import RequestQuotation, PurchaseOrder
from supplier_view.models import PurchaseInvoice
from inventory_view.models import Product, WasteProduct
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F
import matplotlib
import math
from io import BytesIO
import base64
import cv2
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from .forms import ForecastForm
from collections import defaultdict
import plotly.graph_objects as go
from django.db.models.functions import TruncMonth

load_dotenv()
matplotlib.use('agg')


# ===== Dashboard Page ===== #
@login_required(login_url="/login/")
def dashboard(request):
    total_products = Product.objects.filter(status="Active").count()
    low_stock_products = Product.objects.filter(quantity__lte=F('reorder_level')).count()

    # Inventory Dashboard
    total_inventory = Product.objects.aggregate(total=Sum(F('quantity')))['total']
    total_inventory_value = Product.objects.aggregate(total=Sum(F('quantity') * F('cost_price')))['total']
    total_waste = WasteProduct.objects.aggregate(total=Sum('quantity'))['total']
    waste_cost = WasteProduct.objects.aggregate(total=Sum(F('quantity') * F('product__cost_price')))['total']
    top_1_sold_product = SalesInvoiceItem.objects.values('product_name').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold').first()
    top_2_sold_product = SalesInvoiceItem.objects.values('product_name').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold')[1]
    top_3_sold_product = SalesInvoiceItem.objects.values('product_name').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold')[2]
    top_1_wasted_product = WasteProduct.objects.values('product__name').annotate(total_waste=Sum('quantity')).order_by('-total_waste').first()
    top_2_wasted_product = WasteProduct.objects.values('product__name').annotate(total_waste=Sum('quantity')).order_by('-total_waste')[1]
    top_3_wasted_product = WasteProduct.objects.values('product__name').annotate(total_waste=Sum('quantity')).order_by('-total_waste')[2]


    # Procurement Dashboard
    total_ongoing_rq = RequestQuotation.objects.filter(status="Ongoing").count()
    total_pending_pr = PurchaseOrder.objects.filter(status="Pending").count()
    total_approved_pr = PurchaseOrder.objects.filter(status="Approved").count()
    total_delivered_pr = PurchaseOrder.objects.filter(status="Delivered").count()
    total_pi_to_pay = PurchaseInvoice.objects.filter(status="Pending").count()

    return render(request, 'dashboard.html', 
        {'total_products': total_products,
         'low_stock_products': low_stock_products,
         'total_inventory': total_inventory,
         'total_inventory_value': total_inventory_value,
         'total_waste': total_waste,
         'waste_cost': waste_cost,
         'top_1_sold_product': top_1_sold_product,
         'top_2_sold_product': top_2_sold_product,
         'top_3_sold_product': top_3_sold_product,
         'top_1_wasted_product': top_1_wasted_product,
         'top_2_wasted_product': top_2_wasted_product,
         'top_3_wasted_product': top_3_wasted_product,
         'total_ongoing_rq': total_ongoing_rq,
         'total_pending_pr': total_pending_pr,
         'total_approved_pr': total_approved_pr,
         'total_delivered_pr': total_delivered_pr,
         'total_pi_to_pay': total_pi_to_pay,})
# =============================================== #


# ===== Low Stock Products Page ===== #
@login_required(login_url="/login/")
def low_stock_products(request):
    product_instance = Product.objects.filter(quantity__lte=F('reorder_level'))

    return render(request, 'low_stock_products.html', {'product_instance': product_instance})
# =============================================== #

def generate_monthly_sales_graph():
    # Aggregate sales data by month
    monthly_sales = (
        SalesInvoice.objects.filter(status="Paid")
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(total_sales=Sum("total_amount_with_vat"))
        .order_by("month")
    )

    months = [entry["month"].strftime("%B %Y") for entry in monthly_sales]
    totals = [entry["total_sales"] for entry in monthly_sales]

    # Create a bar graph using Plotly
    fig = go.Figure(
        data=[
            go.Bar(
                x=months,
                y=totals,
                marker=dict(color="rgba(55, 128, 191, 0.7)"),
                name="Monthly Sales",
            )
        ]
    )
    fig.update_layout(
        title="Total Sales Per Month",
        xaxis_title="Month",
        yaxis_title="Sales Amount",
        template="plotly_dark",
        xaxis=dict(tickangle=-45),
        margin=dict(l=40, r=40, t=40, b=80),
    )
    return fig.to_html(full_html=False)

# ===== Financial Dashboard Page ===== #
class ForecastForm(forms.Form):
    FORECAST_PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    forecast_period = forms.ChoiceField(choices=FORECAST_PERIOD_CHOICES, initial='daily')

@login_required(login_url="/login/")
def financial_dashboard(request):
    # Total revenue
    total_revenue = SalesInvoice.objects.filter(status='Paid').aggregate(total=Sum('total_amount_with_vat'))['total'] or 0

    today = timezone.now().date()

    # Daily Sale (for today)
    daily_sales = SalesInvoice.objects.filter(status='Paid', transaction_date=today).aggregate(total_sales=Sum('total_amount_with_vat'))['total_sales'] or 0

    first_day_of_month = today.replace(day=1)

    # Monthly Sales
    monthly_sales = SalesInvoice.objects.filter(status='Paid', transaction_date__gte=first_day_of_month).aggregate(total_sales=Sum('total_amount_with_vat'))['total_sales'] or 0

    first_day_of_year = today.replace(month=1, day=1)

    # Yearly Sales
    yearly_sales = SalesInvoice.objects.filter(status='Paid', transaction_date__gte=first_day_of_year).aggregate(total_sales=Sum('total_amount_with_vat'))['total_sales'] or 0

    # Get historical sales data for plotting
    sales_data = SalesInvoice.objects.filter(status='Paid').order_by('transaction_date')

    dates = [sale.transaction_date for sale in sales_data]
    sales = [sale.total_amount_with_vat for sale in sales_data]

    # Handle the forecast form
    forecast_form = ForecastForm(request.POST or None)
    forecast_period = 'monthly'  # Default forecast period
    if forecast_form.is_valid():
        forecast_period = forecast_form.cleaned_data['forecast_period']

    # Determine the number of forecast days based on the selected period
    if forecast_period == 'weekly':
        forecast_days = 35  # 5 weeks
    elif forecast_period == 'monthly':
        forecast_days = 150  # 5 months
    elif forecast_period == 'yearly':
        forecast_days = 1825  # 5 years
    elif forecast_period == 'daily':
        forecast_days = 7  # 7 days
    else:
        forecast_days = 150  # Default

    # Generate forecasted sales
    if len(sales) > 0:
        avg_daily_sales = sum(sales) / len(sales)
    else:
        avg_daily_sales = 0

    forecast_dates = [today + timedelta(days=i) for i in range(1, forecast_days + 1)]
    forecast_sales = [avg_daily_sales * (i + 1) for i in range(forecast_days)]

    # Combine historical sales and forecast data
    all_dates = dates + forecast_dates
    all_sales = sales + forecast_sales

    # Sales Over Time Graph with Forecast using Plotly
    fig_sales = go.Figure()

    # Actual sales
    fig_sales.add_trace(go.Scatter(
        x=dates,
        y=sales,
        mode='markers',
        name='Actual Sales',
        marker=dict(color='blue'),
        text=[f"Sales: {sale}" for sale in sales],  # Hover text showing sales amount
        hoverinfo='text'  # Display text on hover
    ))

    # Forecasted sales
    fig_sales.add_trace(go.Scatter(
        x=forecast_dates,
        y=forecast_sales,
        mode='lines',
        name=f'{forecast_period.capitalize()} Forecast',
        line=dict(color='green', dash='dash'),
        hoverinfo='none'
    ))

    # Aggregate sales by date for the second graph
    aggregated_sales = defaultdict(float)
    for sale in sales_data:
        aggregated_sales[sale.transaction_date] += float(sale.total_amount_with_vat)

    dates_aggregated = sorted(aggregated_sales.keys())  # Sort the dates
    sales_aggregated = [aggregated_sales[date] for date in dates_aggregated]

    # Linear regression
    regression_line = []
    if len(dates_aggregated) > 1:
        numeric_dates = [mdates.date2num(date) for date in dates_aggregated]
        sales_float = [float(sale) for sale in sales_aggregated]
        slope, intercept = np.polyfit(numeric_dates, sales_float, 1)
        regression_line = [slope * date + intercept for date in numeric_dates]

    # Sales with Regression Line using Plotly
    fig_regression = go.Figure()

    # Aggregated sales data
    fig_regression.add_trace(go.Scatter(
        x=dates_aggregated,
        y=sales_aggregated,
        mode='markers',
        name='Aggregated Sales',
        marker=dict(color='blue'),
        text=[f"Sales: {sale}" for sale in sales_aggregated],  # Hover text showing sales amount
        hoverinfo='text'  # Display text on hover
    ))

    # Regression line
    if regression_line:
        fig_regression.add_trace(go.Scatter(
            x=dates_aggregated,
            y=regression_line,
            mode='lines',
            name='Regression Line',
            line=dict(color='red', dash='dash')
        ))

    
    # Layout for both graphs (Sales Over Time and Regression Graph)
    fig_sales.update_layout(
        title="Sales Over Time with Forecast",
        xaxis_title="Date",
        yaxis_title="Sales Amount",
        template="plotly_dark",
        xaxis=dict(tickformat="%Y-%m-%d"),
        dragmode='pan',  # Disable panning and enable zooming
        hovermode='closest',
        margin=dict(l=40, r=40, t=40, b=40),  # Increased margin to avoid overlap

    )

    fig_regression.update_layout(
        title="Sales with Regression Line",
        xaxis_title="Date",
        yaxis_title="Sales Amount",
        dragmode='pan',
        template="plotly_dark",
        hovermode="closest",
        margin=dict(l=40, r=40, t=40, b=40),  # Increased margin to avoid overlap
        
    )

    # Convert both figures to HTML for embedding
    line_graph = fig_sales.to_html(full_html=False,)
    blank_line_graph = fig_regression.to_html(full_html=False)

    bar_graph = generate_monthly_sales_graph()
    
    return render(request, 'financial_dashboard.html', {
        'total_revenue': total_revenue,
        'daily_sales': daily_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
        'line_graph': line_graph,  # Embed Sales Over Time graph
        'blank_line_graph': blank_line_graph,  # Embed Aggregated Sales with Regression graph
        'forecast_form': forecast_form,
        "bar_graph": bar_graph,
    })
# ============================================== #
