from django.contrib import admin

from .models import GoldMaster
from .models import TesterMaster
from .models import ParamMaster
from .models import ParamSetting
from .models import GoldSetting
from .models import PerformSetting
from .models import RuleMaster
from .models import PerformExecute
from .models import PerformingTracking
from .models import PerformingDetail
from .models import RuleMaster
from .models import OperationMaster
from .models import ProductionBatchMaster
from .models import ProductionBatchDetails


class BatchDetailsInline(admin.TabularInline):
    model = ProductionBatchDetails
    extra = 1

class GoldSettingInline(admin.TabularInline):
    model = GoldSetting
    extra = 1


class TesterSettingInline(admin.TabularInline):
    model = GoldSetting
    extra = 1


class PerformingDetailInline(admin.TabularInline):
    model = PerformingDetail
    extra = 0


class PerformingInline(admin.TabularInline):
    model = PerformSetting
    extra = 0


class ProductionBatchMasterAdmin(admin.ModelAdmin):
    search_fields = ['batchname']
    list_filter = ['model']
    list_display = ('batchname','description','model', 'datetime','active')
    fieldsets = [
        (None,               {'fields': ['batchname']}),
        ('Performing information', {'fields': ['batchname','description','model'], 'classes': ['collapse']})
    ]
    inlines = [BatchDetailsInline]

admin.site.register(ProductionBatchMaster,ProductionBatchMasterAdmin)


class PerformingTrackAdmin(admin.ModelAdmin):
    search_fields = ['tester_name']
    list_filter = ['datetime','type','station','tester_name']
    list_display = ('sn','tester_name','station', 'datetime','result','perform_id')
    fieldsets = [
        (None,               {'fields': ['tester_name']}),
        ('Performing information', {'fields': ['ticket','sn','model','station','tester_name','type'], 'classes': ['collapse']})
    ]
    readonly = ['sn']
    inlines = [PerformingDetailInline]

admin.site.register(PerformingTracking,PerformingTrackAdmin)


class OperatorAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['name','group', 'datetime']
    list_display = ('name','group','datetime','active')

admin.site.register(OperationMaster,OperatorAdmin)


class TesterAdmin(admin.ModelAdmin):
    search_fields = ['tester_name']
    list_filter = ['group','location', 'datetime']
    list_display = ('tester_name','location','group','control',
                    'schedule_on','last_execute_date','is_on_due','is_spc_passed')
    fieldsets = [
        ('Tester information', {'fields': ['tester_name','group',('description','active')]}),
        ('SPC Setting', {'fields': ['control'], 'classes': ['collapse']})
    ]

    inlines = [PerformingInline,GoldSettingInline]


admin.site.register(TesterMaster,TesterAdmin)


class GoldAdmin(admin.ModelAdmin):
    list_filter = ['datetime','model']
    list_display = ('sn', 'model', 'description', 'datetime', 'active')
    fieldsets = [
        (None,               {'fields': ['sn']}),
        ('Golden Unit information', {'fields': ['model','description','active'], 'classes': ['collapse']})
    ]
    inlines = [TesterSettingInline]


class ParamAdmin(admin.ModelAdmin):
    search_fields=['param_name']
    list_filter = ['datetime','group']
    list_display = ('param_name','group', 'description', 'spc_required', 'datetime', 'active')
    fieldsets = [
        (None,               {'fields': ['param_name']}),
        ('Parameter information', {'fields': ['group','description', ('unit_name', 'unit_power'), 'spc_required', 'active'], 'classes': ['collapse']})
    ]


class ParamSettingAdmin(admin.ModelAdmin):
    search_fields=['param_name__param_name','tester_name__tester_name']
    list_filter = ['tester_name','param_name','model', 'control_side']
    list_display = ('tester_name','param_name','model', 'control_side', 'active')
    fieldsets = [
        (None,               {'fields': [('tester_name','param_name')]}),
        ('Parameter Setting information', {'fields': [('model','control_side'),
                                                      ('ucl1s','ucl2s','ucl'),
                                                      'cl',
                                                      ('lcl1s','lcl2s','lcl'),
                                                      'active'], 'classes': ['collapse']})
    ]


class PerformSettingAdmin(admin.ModelAdmin):
    list_filter = ['perform_time']
    list_display = ('tester_name','perform_time','interval_time',
                    'last_perform_datetime','last_perform_result','last_spc_result','require_actions')
    fieldsets = [
        (None,               {'fields': ['tester_name']}),
        ('Setting information', {'fields': [('perform_time','interval_time'),'last_perform_result'
            ,'last_spc_result','require_actions']})
    ]


class PerformingDetailAdmin(admin.ModelAdmin):
    search_fields = ['param_name']
    list_filter = ['datetime','result','spc_result','spc_required','param_name']
    list_display = ('param_name','datetime','result','spc_result','spc_required')
    fieldsets = [
        (None,               {'fields': ['param_name']}),
        ('Perform detail', {'fields': [('lower_limit','min_value'),
                                       ('upper_limit','max_value'),'unit_name',
                                       ('spc_result','spc_required'),'spc_response']})
    ]


class RuleMasterAdmin(admin.ModelAdmin):
    search_fields = ['rule_name']
    list_filter = ['type']
    list_display = ('rule_name','type','data_point_count','sigma_zone','datetime','active')
    fieldsets = [
        (None,               {'fields': ['rule_name']}),
        ('Rule detail', {'fields': ['type','data_point_count','sigma_zone','active']})
    ]


admin.site.register(GoldMaster,GoldAdmin)
admin.site.register(ParamMaster,ParamAdmin)
admin.site.register(ParamSetting,ParamSettingAdmin)
admin.site.register(PerformSetting,PerformSettingAdmin)
admin.site.register(PerformExecute)
admin.site.register(PerformingDetail,PerformingDetailAdmin)
admin.site.register(RuleMaster,RuleMasterAdmin)


