from django import forms
from datetimewidget.widgets import DateTimeWidget
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget
from spc.models import OperationMaster
from spc.models import ParamMaster

from django.contrib.admin.widgets import FilteredSelectMultiple


class ActionForm(forms.Form):
    action_text = forms.CharField(label="Actions",max_length=200,widget=forms.Textarea)


class UnitTrackingForm(forms.Form):
    unit_text = forms.CharField(label="Unit Serial number :", max_length=50, widget=forms.TextInput)


class OperationForm(forms.Form):
    start_date = forms.DateTimeField(widget=DateTimeWidget(usel10n=True))
    end_date = forms.DateTimeField(widget=DateTimeWidget(usel10n=True))
    operation = forms.ModelChoiceField(queryset=OperationMaster.objects.filter(active=True))

    dateTimeOptions = {
        'format': 'mm/dd/yyyy HH:ii P',
        'autoclose': True,
        'showMeridian' : True,
        'todayBtn': True,
        'todayHighlight' : True,
        'minuteStep' : 30
    }
    widgets = {
        #NOT Use localization and set a default format
        'datetime': DateTimeWidget(options=dateTimeOptions)
        }


    #parameter = forms.ModelMultipleChoiceField(queryset=ParamMaster.objects.all(),
    #                                          widget=FilteredSelectMultiple("Parameter",
    #                                                                        is_stacked=False,
    #                                                                        attrs={'rows':'10'}))






