from rest_framework import serializers
from .models import PerformingTracking
from .models import PerformingDetail
from .models import PerformingActionLog
from .models import ParamSetting
from .timeZone import DateTimeTzAwareField



class PerformTrakingSerializer(serializers.ModelSerializer):
   # parameters = PerformDetailSerializer(read_only=True, source="param_set", many=True)
    datetime = DateTimeTzAwareField()
    class Meta:
        model = PerformingTracking
        fields = ('perform_id', 'sn', 'model', 'station','datetime','tester_name','user_id')


class PerformDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PerformingDetail
        fields = ('param_name','result','lower_limit','upper_limit','unit_name','min_value','max_value',
                  'spc_required','spc_result','spc_response')


class PerformActionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PerformingActionLog
        fields = ('datetime','action_details','user_id')


class ParamSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParamSetting
        fields = ('id','tester_name','param_name','model','control_side',
                  'ucl2s','ucl1s','ucl','cl','lcl2s','lcl1s','lcl')
