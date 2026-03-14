from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'input-file'}),
        }


class AvatarEditorForm(forms.Form):
    """Form for handling cropped avatar data"""
    avatar_data = forms.CharField(widget=forms.HiddenInput())
    
    def clean_avatar_data(self):
        data = self.cleaned_data.get('avatar_data')
        if not data:
            raise forms.ValidationError('Пожалуйста, загрузите и обрежьте аватар')
        return data
