import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from pos_view.models import SalesInvoice, SalesInvoiceItem
from procurement_view.models import PurchaseOrder
from inventory_view.models import Product
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

load_dotenv()
matplotlib.use('agg')


# ===== Dashboard Page ===== #
@login_required(login_url="/login/")
def dashboard(request):
    total_products = Product.objects.all().count()
    pending_orders = PurchaseOrder.objects.filter(status="Pending").count()
    low_stock_products = Product.objects.filter(quantity__lte=F('reorder_level')).count()

    categories = os.environ.get('PRODUCT_CATEGORIES').split(',')
    product_category = []
    product_category_qty = []

    for category in categories:
        # filter objects per category then summing all quantity for same categories
        total_qty = Product.objects.filter(category=category).aggregate(total=Sum('quantity', default=0))
        product_category.append(category)
        product_category_qty.append(total_qty['total'])

        # Check for None or NaN values
        qty = total_qty['total']
        if qty is None or math.isnan(qty):
            qty = 0 # Placeholder

        product_category_qty.append(qty)

        if not any(product_category_qty):
            product_category_qty = [1]  # Placeholder
            product_category = ["No Data"]

    # just setting the pie chart specifications
    plt.figure(figsize=(4, 4))
    plt.pie(product_category_qty, labels=None,  autopct='%1.1f%%',  pctdistance=1.15, textprops={'fontsize': 8})
    plt.legend(labels=product_category, title="Categories", loc="upper right", bbox_to_anchor=(2, 1), fontsize=8)

    # for donut circle chart
    centre_circle = plt.Circle((0,0), 0.7, color='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # saving plotted pie chart to be able to render in html
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.1)
    buffer.seek(0)
    pie_chart_img = buffer.getvalue()
    plt.close()

    pie_chart = base64.b64encode(pie_chart_img)
    pie_chart = pie_chart.decode('utf-8')

    return render(request, 'dashboard.html', 
        {'total_products': total_products,
         'pending_orders': pending_orders,
         'low_stock_products': low_stock_products,
         'pie_chart': pie_chart})
# =============================================== #


# ===== Low Stock Products Page ===== #
@login_required(login_url="/login/")
def low_stock_products(request):
    product_instance = Product.objects.filter(quantity__lte=F('reorder_level'))

    return render(request, 'low_stock_products.html', {'product_instance': product_instance})
# =============================================== #


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
        updatemenus=[{
            'buttons': [
                {
                    'label': 'Daily',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(days=7), today]]
                },
                {
                    'label': 'Weekly',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(weeks=5), today]]
                },
                {
                    'label': 'Monthly',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(weeks=4*5), today]]
                },
                {
                    'label': 'Yearly',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(days=365), today]]
                }
            ],
            'direction': 'down',  # Keep direction down (vertical stack)
            'showactive': True,
            'x': 1.0,  # Align horizontally using x
            'xanchor': 'left',
            'y': .80,
            'yanchor': 'top',
            'pad': {'t': 10, 'r': 10}  # Add padding to move the dropdown away from the hover and zoom buttons
        }]

    )

    fig_regression.update_layout(
        title="Sales with Regression Line",
        xaxis_title="Date",
        yaxis_title="Sales Amount",
        dragmode='pan',
        template="plotly_dark",
        hovermode="closest",
        margin=dict(l=40, r=40, t=40, b=40),  # Increased margin to avoid overlap
        updatemenus=[{
            'buttons': [
                {
                    'label': 'Daily',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(days=7), today]]
                },
                {
                    'label': 'Weekly',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(weeks=5), today]]
                },
                {
                    'label': 'Monthly',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(weeks=4*5), today]]
                },
                {
                    'label': 'Yearly',
                    'method': 'relayout',
                    'args': ['xaxis.range', [today - timedelta(days=365), today]]
                }
            ],
            'direction': 'down',  # Keep direction down (vertical stack)
            'showactive': True,
            'x': 1.0,  # Align horizontally using x
            'xanchor': 'left',
            'y': .80,
            'yanchor': 'top',
            'pad': {'t': 10, 'r': 10}  # Add padding to move the dropdown away from the hover and zoom buttons
        }]
    )

    # Convert both figures to HTML for embedding
    line_graph = fig_sales.to_html(full_html=False)
    blank_line_graph = fig_regression.to_html(full_html=False)

    return render(request, 'financial_dashboard.html', {
        'total_revenue': total_revenue,
        'daily_sales': daily_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
        'line_graph': line_graph,  # Embed Sales Over Time graph
        'blank_line_graph': blank_line_graph,  # Embed Aggregated Sales with Regression graph
        'forecast_form': forecast_form,
    })
# ============================================== #
