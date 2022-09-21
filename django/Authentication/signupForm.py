from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

"""
This is the collection of forms to be use in a website.
Also can customize the default form that django gives us.
"""


class CreateManagerForm(UserCreationForm):
    username = forms.CharField(max_length=40, help_text="Username")
    email = forms.EmailField(max_length=100, help_text="Email", required=False)

    def __init__(self, *args, **kwargs):
        super(CreateManagerForm, self).__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        self.fields["password1"].widget.attrs["autocomplete"] = "off"
        self.fields["password2"].widget.attrs["autocomplete"] = "off"

    class Meta:
        model = User
        fields = ["username", "email"]
