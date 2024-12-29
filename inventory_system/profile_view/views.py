from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.conf import settings
from django.contrib.auth.models import User
from login_view.models import UserPermission, CompanyProfile
from .forms import UserProfileForm, PasswordChangeForm,CompanyProfileForm
from django.utils import timezone


@login_required(login_url=settings.LOGIN_URL)
def edit_profile(request):
    user_permission = UserPermission.objects.get(user=request.user)
    role = user_permission.role

    user_form = UserProfileForm(request.POST or None, instance=request.user)
    company_profile = CompanyProfile.objects.get(user=request.user)
    supplier_form = CompanyProfileForm(request.POST or None, instance=company_profile)

    if request.method == 'POST':
        if user_form.is_valid():
            if User.objects.exclude(id=request.user.id).filter(username=user_form.cleaned_data['username']).exists(): 
                user_form.add_error('username', 'This username is already taken.')

            else:
                if company_profile is None or company_profile.last_edited:
                    time_difference = timezone.now().date() - company_profile.last_edited

                    if time_difference.days < 7:
                        days_left = 7 - time_difference.days

                        messages.error(request, f"You can edit your profile again in {days_left} days.")
                        return redirect('edit_profile')
            
                    if supplier_form.is_valid():
                        company_name = supplier_form.cleaned_data['company_name']
                        company_contact = supplier_form.cleaned_data['company_contact']

                        if CompanyProfile.objects.exclude(id=company_profile.id).filter(company_name=company_name).exists():
                            supplier_form.add_error('company_name', 'This company name is already taken.')

                        elif CompanyProfile.objects.exclude(id=company_profile.id).filter(company_contact=company_contact).exists():
                            supplier_form.add_error('company_contact', 'This company contact is already taken.')

                        else:
                            supplier_form.save()

                user_form.save()
                company_profile.last_edited = timezone.now().date()
                company_profile.save()
            
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('edit_profile')
                
        else:
            messages.error(request, "Please correct the errors in the user form.")

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'supplier_form': supplier_form,
        'role': role,
    })


@login_required(login_url=settings.LOGIN_URL)
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)

        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']

            user = authenticate(request, username=request.user.username, password=current_password)
            
            if user is not None:
                user.set_password(new_password)
                user.save()

                update_session_auth_hash(request, user)

                messages.success(request, 'Your password has been updated successfully.')
                return redirect('change_password')
            else:
                form.add_error('current_password', 'Your current password is incorrect.')
    else:
        form = PasswordChangeForm()

    return render(request, 'change_password.html', {'form': form})