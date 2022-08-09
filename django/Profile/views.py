from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .edit_profile_form import EditProfileForm


# Create your views here.


class Profile(LoginRequiredMixin, View):
    login_url = 'login'
    profile_page = 'Profile/profile.html'
    navbar_colour = {'admin': '#808080',
                     'manager': '#AD9CFF',
                     'marker': '#FF434B',
                     'scanner': '#0F984F'}
    form = EditProfileForm()

    def get(self, request):
        form = EditProfileForm(instance=request.user)
        try:
            user = request.user.groups.all()[0].name
        except IndexError:
            user = None
        if user in Profile.navbar_colour:
            colour = Profile.navbar_colour[user]
        else:
            colour = '#FFFFFF'
            context = {'form': form, 'navbar_colour': colour, 'user_group': user,
                       'email': request.user.email}
            return render(request, self.profile_page, context)
        context = {'form': form, 'navbar_colour': colour, 'user_group': user,
                   'email': request.user.email}
        return render(request, self.profile_page, context, status=200)

    def post(self, request):
        try:
            user = request.user.groups.all()[0].name
        except IndexError:
            user = None
        if user in Profile.navbar_colour:
            colour = Profile.navbar_colour[user]
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            context = {'form': Profile.form, 'navbar_colour': colour, 'user_group': user,
                       'email': request.user.email}
            return render(request, self.profile_page, context, status=200)
