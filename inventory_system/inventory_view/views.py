from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import PerishableProductForm, NonPerishableProductForm, ProductFilterForm
from .models import Product, WasteProduct


# ===== DUMMY PAGE FOR TESTING ===== #
def dummy_page(request):
    return HttpResponse("Welcome to a page.")
# =============================================== #


# ===== ALL PRODUCTS PAGE ===== #
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})
# =============================================== #


# ===== ADDING STOCK CHOICE PAGE ===== #
def add_stock_choice(request):
    return render(request, 'add_stock_choice.html')
# =============================================== #


# ===== ADDING PERISHABLE PRODUCT PAGE ===== #
def add_perishable(request):
    if request.method == "POST":
        form = PerishableProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_list')
        
    else:
        form = PerishableProductForm()

    return render(request, 'add_perishable.html', {'form': form})
# =============================================== #


# ===== ADDING NON-PERISHABLE PRODUCT PAGE ===== #
def add_nonperishable(request):
    if request.method == "POST":
        form = NonPerishableProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_list')
        
    else:
        form = NonPerishableProductForm()

    return render(request, 'add_nonperishable.html', {'form': form})
# =============================================== #


# ===== FILTER ALL PRODUCTS (FOR WASTAGE) PAGE ===== #
def filter_product_list(request):
    form = ProductFilterForm(request.GET)
    products = Product.objects.all()

    if form.is_valid():
        sku = form.cleaned_data.get('sku')
        name = form.cleaned_data.get('name')
        expiration_date = form.cleaned_data.get('expiration_date')

        if sku:
            products = products.filter(sku__icontains=sku)
        if name:
            products = products.filter(name__icontains=name)
        if expiration_date:
            products = products.filter(expiration_date=expiration_date)

    return render(request, 'filter_product_list.html', {'form': form, 'products': products})
# =============================================== #


# ===== ADD PRODUCT TO WASTAGE PAGE ===== #
def add_to_waste(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        waste_product = WasteProduct(
            name=product.name,
            description=product.description,
            sku=product.sku,
            category=product.category,
            price=product.price,
            cost_price=product.cost_price,
            unit_of_measurement=product.unit_of_measurement,
            weight=product.weight,
            dimensions=product.dimensions,
            color=product.color,
            material=product.material,
            supplier_name=product.supplier_name,
            date_added=product.date_added,
            expiration_date=product.expiration_date,
            batch_number=product.batch_number,
            brand=product.brand,
        )

        waste_product.save()
        product.delete()

        return redirect('filter_product_list')
    
    return render(request, 'add_to_waste.html', {'product': product})
# =============================================== #
