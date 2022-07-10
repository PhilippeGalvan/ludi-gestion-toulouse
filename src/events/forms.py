from django import forms


class IndividualCandidacyForm(forms.Form):
    player = forms.BooleanField(label='Joueur ?', required=False)
    speaker = forms.BooleanField(label='MC ?', required=False)
    arbiter = forms.BooleanField(label='Arbitre ?', required=False)
    disk_jockey = forms.BooleanField(label='DJ ?', required=False)

    def clean(self):
        cleaned_data = super().clean()
        if not any([cleaned_data["player"], cleaned_data["speaker"], cleaned_data["arbiter"], cleaned_data["disk_jockey"]]):
            raise forms.ValidationError('At least one role is required to create a candidacy request')
        return cleaned_data
