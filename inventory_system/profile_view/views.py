from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from login_view.models import UserPermission, Supplier
from .forms import UserProfileForm, SupplierProfileForm


@login_required(login_url=settings.LOGIN_URL)
def edit_profile(request):
    user_permission = UserPermission.objects.get(user=request.user)
    role = user_permission.role

    user_form = UserProfileForm(request.POST or None, instance=request.user)
    supplier_form = None
    if role == 'supplier':
        supplier = Supplier.objects.get(user=request.user)
        supplier_form = SupplierProfileForm(request.POST or None, instance=supplier)

    if request.method == 'POST':
        if user_form.is_valid():
            if User.objects.exclude(id=request.user.id).filter(username=user_form.cleaned_data['username']).exists():
                user_form.add_error('username', 'This username is already taken.')
            
            else:
                user_form.save()

                if role == 'supplier' and supplier_form:
                    if supplier_form.is_valid():
                        company_name = supplier_form.cleaned_data['supplier_company_name']
                        company_contact = supplier_form.cleaned_data['supplier_company_contact']

                        if Supplier.objects.exclude(id=supplier.id).filter(supplier_company_name=company_name).exists():
                            supplier_form.add_error('supplier_company_name', 'This company name is already taken.')

                        elif Supplier.objects.exclude(id=supplier.id).filter(supplier_company_contact=company_contact).exists():
                            supplier_form.add_error('supplier_company_contact', 'This company contact is already taken.')

                        else:
                            supplier_form.save()

                            messages.success(request, "Your profile has been updated successfully!")
                            return redirect('edit_profile')
                        
                    else:
                        messages.error(request, "Please correct the errors in the supplier form.")

                else:
                    messages.success(request, "Your profile has been updated successfully!")
                    return redirect('edit_profile')
                
        else:
            messages.error(request, "Please correct the errors in the user form.")

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'supplier_form': supplier_form,
        'role': role,
    })
