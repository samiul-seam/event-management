from django import forms
from events.models import Event, Category
from django.contrib.auth.models import User


class StyledFormMixin:
    """Mixin to apply style to form fields"""

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': f"{self.default_classes} resize-none",
                    'placeholder': f"Enter {field.label.lower()}",
                    'rows': 5
                })
            elif isinstance(field.widget, forms.SelectDateWidget):
                field.widget.attrs.update({
                    "class": "border-2 border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500"
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({
                    'class': "border-2 border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500"
                })
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({
                    'class': self.default_classes
                })
            else:
                field.widget.attrs.update({'class': self.default_classes})


class EventModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category', 'asset', 'participants']
        widgets = {
            'date': forms.SelectDateWidget(),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'participants': forms.CheckboxSelectMultiple(),
        }
 
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("categories", None)
        participants = kwargs.pop("participants", None)
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = categories or Category.objects.all()
        self.fields['participants'].queryset = participants or User.objects.all()


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'border rounded-md px-3 py-2 w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'border rounded-md px-3 py-2 w-full'}),
            'email': forms.EmailInput(attrs={'class': 'border rounded-md px-3 py-2 w-full'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name' , 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'border rounded p-2 w-full'}),
            'name': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'})
        }