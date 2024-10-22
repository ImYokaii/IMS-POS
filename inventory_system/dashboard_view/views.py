import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from inventory_view.models import Product
from .models import ProductInstance
from .forms import ReorderLevelForm, SearchFilterForm
from .utils import search_filter_product_list
from django.db.models import Sum, F
import matplotlib.pyplot as plt
import matplotlib
import math
from io import BytesIO
import base64
from django.shortcuts import render
import cv2
from django.shortcuts import render
from django.http import JsonResponse

load_dotenv()
matplotlib.use('agg')

# ===== Dashboard Page ===== #
def dashboard(request):
    total_products = Product.objects.all().count()

    low_stock_products = ProductInstance.objects.filter(quantity__lte=F('reorder_level')).count()

    categories = os.environ.get('PRODUCT_CATEGORIES').split(',')
    product_category = []
    product_category_qty = []

    for category in categories:
        # filter objects per category then summing all quantity for same categories
        total_qty = ProductInstance.objects.filter(category=category).aggregate(total=Sum('quantity', default=0))
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

    return render(request, 'dashboard.html', {'total_products': total_products,
                                              'low_stock_products': low_stock_products,
                                              'pie_chart': pie_chart})
# =============================================== #


# ===== Product Levels Page ===== #
def product_levels(request):
    form = SearchFilterForm(request.POST)
    
    if form.is_valid():
        name = form.cleaned_data.get('name')
        category = form.cleaned_data.get('category')

        product_instance = search_filter_product_list(name, category)

    return render(request, 'product_levels.html', {'product_instance': product_instance, 'form': form})
# =============================================== #


# ===== Dashboard Page ===== #
def edit_reorder_levels(request, product_id):
    product = get_object_or_404(ProductInstance, id=product_id)

    if request.method == "POST":
        form = ReorderLevelForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect('product_levels')
        
    else:
        form = ReorderLevelForm(instance=product)

    return render(request, 'edit_reorder_levels.html', {'product': product, 'form': form})
# =============================================== #


# ===== Low Stock Products Page ===== #
def low_stock_products(request):
    product_instance = ProductInstance.objects.filter(quantity__lte=F('reorder_level'))

    return render(request, 'low_stock_products.html', {'product_instance': product_instance})
# =============================================== #

# ===== QR Scanner ===== #
class QRCodeScanner:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.detector = cv2.QRCodeDetector()
        self.data = None

    def start_scanning(self):
        ret, img = self.cap.read()
        if not ret:
            print("Failed to grab frame.")
            return None
        
        self.data, _, _ = self.detector.detectAndDecode(img)
        return self.data

    def release_resources(self):
        self.cap.release()
        cv2.destroyAllWindows()

def scan_qr_code(request):
    if request.method == "POST":
        scanner = QRCodeScanner()
        try:
            scanned_value = scanner.start_scanning()
        finally:
            scanner.release_resources()

        if scanned_value:
            return render(request, 'scan_result.html', {'scanned_value': scanned_value})
        else:
            return render(request, 'scan_result.html', {'error': 'No QR code detected.'})

    return render(request, 'scan_qr.html')
