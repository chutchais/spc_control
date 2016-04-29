# Create your models here.
from django.db import models
from django.utils import timezone
import datetime
from datetime import timedelta

from django.db.models import Max
from django.db.models import Min


class OperationMaster(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=255, null=True,blank=True)
    group = models.CharField(max_length=255, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.name


class TesterMaster(models.Model):
    tester_name = models.CharField(max_length=50, primary_key=True)
    location = models.CharField(max_length=20, null=True,blank=True)
    description = models.CharField(max_length=255, null=True,blank=True)
    group = models.CharField(max_length=255, null=True, blank=True)
    control = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.tester_name

    def is_action_pending(self):
        ps = PerformSetting.objects.get(tester_name=self.tester_name)
        return ps.require_actions
    is_action_pending.short_description = 'Has Action pending?'

    def schedule_on(self):
        ps = PerformSetting.objects.get(tester_name=self.tester_name)
        return ps.perform_time
    schedule_on.short_description = 'schedule on (time)'

    def is_on_due(self):
        ps = PerformSetting.objects.get(tester_name=self.tester_name)
        tzaw = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        tzaw_new = tzaw.replace(hour=ps.perform_time.hour, minute=0,second=0)

        #Added by Chutchai on Dec1 , to handle long last run.
        if tzaw_new > timezone.localtime(ps.last_perform_datetime)+  timedelta(hours=ps.interval_time):
            return False

        if datetime.datetime.now().hour >= ps.perform_time.hour :
            if ps.last_perform_result == False :
                #if no last perform, need to Perform test
                return False
            elif ps.last_perform_datetime is None:
                return False
            elif tzaw_new > timezone.localtime(ps.last_perform_datetime) :
                return False
            else:
                return True
        else :
            return True

    is_on_due.boolean = True
    is_on_due.short_description = 'Up to date'

    def is_spc_passed(self):
        ps = PerformSetting.objects.get(tester_name=self.tester_name)
        return ps.last_spc_result
    is_spc_passed.short_description = 'Last Execute SPC result'
    is_spc_passed.allow_tags = True
    is_spc_passed.boolean = True

    #def last_failed_spc(self):
    #    ps = PerformSetting.objects.get(tester_name=self.tester_name)
    #    pd = PerformingDetail.objects.filter(perform_id=ps.perform_id,spc_required=True,spc_result=False)
    #    return pd

    #{'spc_result': True} if pd.count() == 0 else {'spc_result': False ,'perform_id': ps.perform_id}

    #a= timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    #a.replace(hour=ps.perform_time.hour ,minute=0,second=0) > timezone.localtime(ps.last_perform_datetime)
    #def was_execute_spc(self):
    #    ps = PerformSetting.objects.get(tester_name=self.tester_name)
    #    return self.datetime.hour <= ps.perform_time
    #timezone.localtime(timezone.now()) - datetime.timedelta(hours=2)
    #datetime.datetime.now().strftime('%H%M%S')
    #timezone.localtime(timezone.now()).strftime('%H%M%S')
    #timezone.localtime(a.last_perform_datetime).hour

    #was_execute_spc.admin_order_field = 'datetime'
    #was_execute_spc.boolean = True
    #was_execute_spc.short_description = 'Execute SPC?'


    def last_execute_date(self):
        ps = PerformSetting.objects.get(tester_name=self.tester_name)
        return ps.last_perform_datetime
    last_execute_date.short_description = 'Last Execute datetime'
    last_execute_date.allow_tags = True

    def last_perform_id(self):
        ps = PerformSetting.objects.get(tester_name=self.tester_name)
        return ps.perform_id


    def last_execute_result(self):
        ps = PerformSetting.objects.get(tester_name=self.tester_name)
        return ps.last_perform_result
    last_execute_result.short_description = 'Last Execute SPC result?'
    last_execute_result.allow_tags = True
    last_execute_result.boolean = True


class GoldMaster(models.Model):
    sn = models.CharField(verbose_name='Gold Serial number', max_length=50, primary_key=True)
    model = models.CharField(verbose_name='Model', max_length=50, null=True)
    testers = models.ManyToManyField(TesterMaster , through='GoldSetting')
    description = models.CharField(max_length=255, null=True)
    datetime = models.DateTimeField(verbose_name='Created date', auto_now=True)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
            return self.sn


class GoldSetting(models.Model):
    tester_name = models.ForeignKey(TesterMaster)
    sn = models.ForeignKey(GoldMaster)
    description = models.CharField(max_length=255, null=True)
    datetime = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return "%s for %s" % (self.sn, self.tester_name)


class ParamMaster(models.Model):
    param_name = models.CharField(max_length=50, primary_key=True)
    testers = models.ManyToManyField(TesterMaster , through='ParamSetting')
    spc_required = models.BooleanField()
    unit_name = models.CharField(max_length=10,null=True)
    unit_power = models.SmallIntegerField(default=0)
    group = models.CharField(max_length=20,null=True)
    description = models.CharField(max_length=255, null=True)
    datetime = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.param_name


class ParamSetting(models.Model):
    CTRL_SIDE = (
        ('MIN', 'Min Side'),
        ('MAX', 'Max Side'),
        ('BOTH', 'Both Side'),
    )
    id = models.AutoField(primary_key=True)
    tester_name = models.ForeignKey(TesterMaster)
    param_name = models.ForeignKey(ParamMaster)
    model = models.CharField(verbose_name='Model',max_length=50, null=True)
    control_side = models.CharField(max_length=4, null=True, choices=CTRL_SIDE)
    ucl = models.FloatField(verbose_name='Upper line(3s)', default=0.0)
    ucl2s = models.FloatField(verbose_name='Upper line(2s)', default=0.0)
    ucl1s = models.FloatField(verbose_name='Upper line(1s)', default=0.0)
    cl = models.FloatField(verbose_name='Center line', default=0.0)
    lcl1s = models.FloatField(verbose_name='Lower line(1s)', default=0.0)
    lcl2s = models.FloatField(verbose_name='Lower line(2s)', default=0.0)
    lcl = models.FloatField(verbose_name='Lower line(3s)', default=0.0)
    datetime = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return "%s" % (self.param_name)


class PerformSetting(models.Model):
    tester_name = models.OneToOneField(TesterMaster,
                                       on_delete=models.CASCADE,
                                       primary_key=True,)
    perform_time = models.TimeField(default="00:00")
    interval_time = models.IntegerField(verbose_name='Repeat Every(hr)', default=24)
    last_perform_datetime = models.DateTimeField(default=timezone.now, blank= True, null= True)
    last_perform_result = models.BooleanField()
    perform_id = models.CharField(max_length=50 ,blank= True, null= True)
    datetime = models.DateTimeField(default=timezone.now)
    last_spc_result = models.BooleanField(default=False)
    require_actions = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return '%s the perform setting' % self.tester_name.tester_name


class SpcRuleMaster(models.Model):
    rule_name = models.CharField(max_length=50, primary_key=True)
    data_point_count = models.IntegerField(default=3)
    sigma_zone = models.IntegerField(default=3)
    out_of_limit = models.BooleanField()
    continuous_mode = models.BooleanField()

    def __str__(self):              # __unicode__ on Python 2
        return self.rule_name


class SpcSetting(models.Model):
    tester_name = models.ForeignKey(TesterMaster)
    rule_name = models.ForeignKey(SpcRuleMaster)
    action = models.BooleanField()
    datetime = models.DateTimeField(auto_now=True)
    active = models.BooleanField()

    def __str__(self):              # __unicode__ on Python 2
        return self.tester_name


class PerformingTracking(models.Model):
    PERFORM_TYPE = [('PROD', 'Production'),
                    ('GR&R', 'Gate Repeat and Reproduce'),
                    ('VALIDATE', 'Validation'), ]
    perform_id = models.AutoField(primary_key=True)
    sn = models.CharField(verbose_name='DUT serial number', max_length=50)
    model = models.CharField(verbose_name='DUT model', max_length=20, null= True)
    station = models.CharField(max_length=20 , blank=True)
    tester_name = models.CharField(verbose_name='Tester Name', max_length=50)
    location = models.CharField(max_length=20, null= True , blank=True)
    ticket = models.CharField(max_length=20 , null= True , blank=True)
    datetime = models.DateTimeField()
    type = models.CharField(max_length=10, null=True, choices=PERFORM_TYPE)
    user_id = models.CharField(max_length=20 ,null=True)
    result = models.BooleanField(default=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.tester_name


class PerformingDetail(models.Model):
    perform_id = models.ForeignKey(PerformingTracking , related_name='perform_set')
    param_name = models.CharField(max_length=50)
    result = models.BooleanField()
    lower_limit = models.FloatField(verbose_name='Lower limit', default=0.0)
    upper_limit = models.FloatField(verbose_name='Upper limit', default=0.0)
    unit_name = models.CharField(max_length=10)
    min_value = models.FloatField(verbose_name='Min value', default=0.0)
    max_value = models.FloatField(verbose_name='Max value', default=0.0)
    datetime = models.DateTimeField()
    spc_required = models.BooleanField(default= False)
    spc_result = models.BooleanField(default= False)
    spc_response = models.TextField(max_length=255, null=True,blank=True)

    def is_master_required(self):
        #pm = ParamMaster.objects.get(param_name=self.param_name)
        try:
            x = ParamMaster.objects.get(param_name=self.param_name)
            return x.spc_required
        except ParamMaster.DoesNotExist:
            return False
        #return pm.spc_required

    #@property
    def excecute_spc(self):
        if self.spc_required:
            #self.perform_id.tester_name
            #pm = PerformingTracking.objects.get(perform_id =self.perform_id_id)
            #pss = ParamSetting.objects.filter(tester_name=pm.tester_name,
            #                                param_name=self.param_name,model=pm.model,active=True)
            pss = ParamSetting.objects.filter(tester_name=self.perform_id.tester_name,
                                              param_name=self.param_name,model=self.perform_id.model
                                              , active=True)
            final_resp = dict()
            #check Param setting before
            if pss.count() == 0:
                final_resp.update({'paramSetting': 'Not found parameter setting'})
                final_result = False
            else:
                final_result = True

            #ps , return more 1 objects
            #perform details -->Min value , Max Value (self.min_value self.max_value)
            #param setting -->1st Rule , ucl,lcl (ps.ucl ,ps.lcl)
            msg = "No Setting -- Passed"

            #get RuleMaster.
            rms = RuleMaster.objects.filter(active=True)
            if rms.count() == 0:
                final_resp.update({'ruleSetting': 'Not found rule setting'})
                final_result = False

            #each parameters setting
            for ps in pss:

                for rm in rms:
                    if rm.type == "OUT_OF_LIMIT":
                        execute_out = self.rule_outOfLimit(float(ps.lcl), float(ps.ucl),
                                                           ps.control_side,rm.rule_name)
                        hit_rule = execute_out.get('hit_rule')
                        execute_res = execute_out.get('execute_response')
                        final_resp.update({'OutOfLimit %s' %ps.control_side :execute_res})
                        if hit_rule:
                            final_result = False

                    if rm.type == "TREND":
                        #rm.data_point_count (tester,parameter)
                        execute_trend = self.rule_Trend(self.perform_id.tester_name,
                                                        self.param_name, rm.data_point_count,
                                                        ps.control_side,rm.rule_name)
                        hit_rule = execute_trend.get('hit_rule')
                        execute_res = execute_trend.get('execute_response')
                        final_resp.update({'Trend %s' %ps.control_side : execute_res})
                        if hit_rule:
                            final_result = False

                    if rm.type == "POINTINROW":
                        #rm.data_point_count (tester,parameter)
                        execute_point = self.rule_pointInRow(self.perform_id.tester_name,
                                                        self.param_name, rm.data_point_count,
                                                        ps.control_side,rm.rule_name,
                                                        ps.lcl1s,ps.ucl1s)
                        hit_rule = execute_point.get('hit_rule')
                        execute_res = execute_point.get('execute_response')
                        final_resp.update({'Point in Row %s' %ps.control_side : execute_res})
                        if hit_rule:
                            final_result = False


            #end for loop

            #update SPC Result
            self.spc_result = final_result
            self.spc_response = final_resp
            self.save()
            #final_resp.update({'final_result':final_result})


            return final_resp

    def rule_outOfLimit(self , vlcl, vucl, vside_control,rule_name):

        is_break_rule = False
        execute_result = ""

        if vside_control == 'MIN':
            #1st Rule
            if (float(self.min_value) < vlcl) or (float(self.min_value) > vucl):
                is_break_rule = True
                execute_result = "Result -- Failed , value =%s (limit =%s ,%s)" % (self.min_value,vlcl,vucl)
            else:
                execute_result = "Result -- Passed"
        elif vside_control == 'MAX':
            #1st Rule
            if (float(self.max_value) < vlcl) or (float(self.max_value) > vucl):
                is_break_rule = True
                execute_result = "Result -- Failed , value =%s (limit =%s ,%s)" % (self.max_value,vlcl,vucl)
            else:
                execute_result = "Result -- Passed"
        elif vside_control == 'BOTH':
            #1st Rule
            execute_result = "Result -- Passed"
            if (self.min_value < vlcl) or (self.min_value > vucl):
                is_break_rule = True
                execute_result = "Result -- Failed , value =%s (limit =%s ,%s)" % (self.min_value,vlcl,vucl)
            if (self.max_value < vlcl) or (self.max_value > vucl):
                is_break_rule = True
                execute_result = "Result -- Failed , value =%s (limit =%s ,%s)" % (self.max_value,vlcl,vucl)

        #Save to PerformExcute table
        #is_break_rule is Negative result , False means SPC passed , True means SPC failed.
        rm = RuleMaster.objects.get(rule_name= rule_name)
        pe = PerformExecute.objects.create(perform_param=self,rule_name=rm,
                                           execute_result=not is_break_rule,
                                           spc_lower_limit=vlcl, spc_upper_limit=vucl,
                                           side=vside_control)
        pe.save()
        return {'hit_rule':is_break_rule ,'execute_response':execute_result}


        #tester_name,param_name,model (self)

    def rule_Trend(self , tester_name, param_name,data_size, vside_control,rule_name):

        pd = PerformingDetail.objects.filter(param_name=param_name,
                                             perform_id__tester_name=tester_name).order_by('-datetime')[:data_size]

        if vside_control == 'MIN':
            data_list = " ,".join(str(s.min_value) for s in pd if s is not None)
        else:
            data_list = " ,".join(str(s.max_value) for s in pd if s is not None)

        is_break_rule = True
        execute_result = "Result -- Failed ,Data %s" % data_list

        if pd.count() < data_size:
            is_break_rule = False
            execute_result = "Data is not enough to calculate trend"
        else:
            #check Trend
            if pd[0].min_value == pd[1].min_value:
                if pd[1].min_value < pd[2].min_value:
                    mintrend = "UP"
                else:
                    mintrend = "DOWN"
            elif pd[0].min_value > pd[1].min_value:
                mintrend = "DOWN"
            else :
                mintrend = "UP"

            if pd[0].max_value == pd[1].max_value:
                if pd[1].max_value < pd[2].max_value:
                    maxtrend = "UP"
                else:
                    maxtrend = "DOWN"
            elif pd[0].max_value > pd[1].max_value:
                maxtrend = "DOWN"
            else :
                maxtrend = "UP"

            if vside_control == 'MIN':
                #1st Rule
                execute_result = "Result -- Failed ,Data %s" % data_list

                for p in range(len(pd)-1):
                    if mintrend == "UP": #Up trend
                        if pd[p+1].min_value <= pd[p].min_value:
                            is_break_rule= False
                            execute_result = "Result -- Passed ,Data : %s" % data_list
                            break
                    else: #Down trend
                        if pd[p+1].min_value >= pd[p].min_value:
                            is_break_rule= False
                            execute_result = "Result -- Passed ,Data : %s" % data_list
                            break



            elif vside_control == 'MAX':
                #1st Rule
                execute_result = "Result -- Failed ,Data %s" % data_list
                for p in range(len(pd)-1):
                    if maxtrend == "UP":
                        if pd[p+1].max_value <= pd[p].max_value:
                            is_break_rule = False
                            execute_result = "Result -- Passed ,Data %s" % data_list
                            break
                    else:
                        if pd[p+1].max_value >= pd[p].max_value:
                            is_break_rule = False
                            execute_result = "Result -- Passed ,Data %s" % data_list
                            break

            elif vside_control == 'BOTH':
                #1st Rule
                is_break_rule = False
                execute_result = "Result -- Passed"


        #Save to PerformExcute table
        #is_break_rule is Negative result , False means SPC passed , True means SPC failed.
        rm = RuleMaster.objects.get(rule_name= rule_name)
        pe = PerformExecute.objects.create(perform_param=self,rule_name=rm,
                                           execute_result=not is_break_rule,
                                           spc_lower_limit=pd.count(), spc_upper_limit=data_size,
                                           side=vside_control)
        pe.save()
        return {'hit_rule':is_break_rule ,'execute_response':execute_result}


        #tester_name,param_name,model (self)


    def rule_pointInRow(self , tester_name, param_name,data_size, vside_control,
                        rule_name, sigma_zone_min ,sigma_zone_max):

        pd = PerformingDetail.objects.filter(param_name=param_name,
                                             perform_id__tester_name=tester_name).order_by('-datetime')[:data_size]

        if vside_control == 'MIN':
            data_list = " ,".join(str(s.min_value) for s in pd if s is not None)
        else:
            data_list = " ,".join(str(s.max_value) for s in pd if s is not None)

        is_break_rule = True
        execute_result = "Result -- Failed ,Data %s" % data_list

        if pd.count() < data_size:
            is_break_rule = False
            execute_result = "Data is not enough to calculate %s points in row" % data_size
        else:

            if vside_control == 'MIN':
                min_point = pd.aggregate(Min('min_value')).get('min_value__min') or 0
                max_point = pd.aggregate(Max('min_value')).get('min_value__max') or 0
                execute_result = "Result -- Failed ,Data %s" % data_list
                if (float(min_point) <= sigma_zone_max) or (float(max_point) >= sigma_zone_min ):
                    is_break_rule = False
                    execute_result = "Result -- Passed ,Data : %s" % data_list

            elif vside_control == 'MAX':
                min_point = pd.aggregate(Min('max_value')).get('max_value__min') or 0
                max_point = pd.aggregate(Max('max_value')).get('max_value__max') or 0
                execute_result = "Result -- Failed ,Data %s" % data_list

                if float(min_point) <= sigma_zone_max and float(min_point) >= sigma_zone_min :
                    is_break_rule = False
                    execute_result = "Result -- Passed ,Data : %s" % data_list

                if float(max_point) <= sigma_zone_max and float(max_point) >= sigma_zone_min :
                    is_break_rule = False
                    execute_result = "Result -- Passed ,Data : %s" % data_list


            elif vside_control == 'BOTH':
                #1st Rule
                is_break_rule = False
                execute_result = "Result -- Passed"


        #Save to PerformExcute table
        #is_break_rule is Negative result , False means SPC passed , True means SPC failed.
        rm = RuleMaster.objects.get(rule_name= rule_name)
        pe = PerformExecute.objects.create(perform_param=self,rule_name=rm,
                                           execute_result=not is_break_rule,
                                           spc_lower_limit=sigma_zone_min, spc_upper_limit=sigma_zone_max,
                                           side=vside_control)
        pe.save()
        return {'hit_rule':is_break_rule ,'execute_response':execute_result}


        #tester_name,param_name,model (self)

    def __str__(self):              # __unicode__ on Python 2
        return self.param_name


class RuleMaster(models.Model):
    SPC_TYPE = (
        ('OUT_OF_LIMIT', 'Out of Limit'),
        ('TREND', 'Trend of data'),
        ('POINTINROW','Point in Row')
    )
    rule_name = models.CharField(max_length=50,primary_key=True)
    data_point_count = models.IntegerField(default=1)
    type = models.CharField(max_length=20, null=True, choices=SPC_TYPE)
    sigma_zone = models.IntegerField(default=3)
    datetime = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.rule_name


class PerformExecute(models.Model):
    perform_param = models.ForeignKey(PerformingDetail)
    rule_name = models.ForeignKey(RuleMaster)
    execute_result = models.BooleanField(default= False)
    spc_lower_limit = models.FloatField(verbose_name='SPC lower limit', default=0.0, blank=True)
    spc_upper_limit = models.FloatField(verbose_name='SPC Upper limit', default=0.0, blank=True)
    side = models.CharField(max_length=20, default='MIN')#min,max or both


    def __str__(self):              # __unicode__ on Python 2
        return "%s of %s" % (self.rule_name,self.side)


class PerformingActionLog(models.Model):
    perform_id = models.ForeignKey(PerformingTracking , related_name='actions_set')
    tester_name = models.CharField(verbose_name='Tester Name', max_length=50)
    datetime = models.DateTimeField(auto_now_add= True)
    result = models.BooleanField(default=False)
    action_details = models.TextField(max_length=255, null=True ,blank=True)
    user_id = models.CharField(max_length=20 ,null=True,blank=True)


class ProductionBatchMaster(models.Model):
    batchname = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=255, null=True,blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.batchname


class ProductionBatchDetails(models.Model):
    sn = models.CharField(verbose_name='DUT serial number', max_length=50)
    batch = models.ForeignKey(ProductionBatchMaster,related_name='batch_set')
    datetime = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.sn

#sn = models.CharField(verbose_name='DUT serial number', max_length=50)










