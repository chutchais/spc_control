from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PerformingTracking
from .models import PerformingDetail
from .models import PerformSetting
from .models import ParamSetting
from .models import TesterMaster
from .models import ParamMaster
from .models import PerformingActionLog

#test Git

#from rest_framework import serializers
#from rest_framework.parsers import JSONParser

from spc.serializers import PerformTrakingSerializer
from spc.serializers import PerformDetailSerializer
from spc.serializers import ParamSettingSerializer
from spc.serializers import PerformActionsSerializer

import xml.etree.cElementTree as ET
from django.utils import timezone


@api_view(['GET', 'POST'])
def xml_transaction(request):

    if True :
        xml = request.body
        return Response(execute_transaction(xml))
    else:
        return Response("Accept only xml (ODC/SPC compatible)" )


def execute_transaction(xml):
    try:
        root = ET.fromstring(xml)
        #Main data
        ticket = root.findtext('ticket')
        sn = root.findtext('sn')
        model = root.findtext('model')
        station = root.findtext('station')
        testername = root.findtext('testername')
        user = root.findtext('user')
        result = root.findtext('result')
        data_type = root.findtext('type')
        location = root.findtext('location')
        datetime_in = root.findtext('spc/datetime')

        #Modify by Chutchai on April 20,2016
        #To not accect VALIDATE transaction while ActionRequire flag is True
        if data_type == 'VALIDATE':
            ps = PerformSetting.objects.get(tester_name= testername)
            if ps.require_actions:
                return "Not allow to execute data, found action is pending"


        #insert to model
        #xmltrack = PerformingTracking(sn='' , model='', station='', tester_name='', ticket=ticket, type='')
        xmltrack = PerformingTracking()
        xmltrack.sn = sn
        xmltrack.model = model
        xmltrack.station = station
        xmltrack.tester_name = testername
        xmltrack.location= location
        xmltrack.ticket = ticket
        xmltrack.type = data_type
        xmltrack.user_id = user
        xmltrack.result = True if result == 'P' else False
        import datetime
        from django.utils import timezone
        date_in = datetime.datetime.strptime(datetime_in, '%d-%m-%Y %H:%M:%S')
        xmltrack.datetime = timezone.make_aware(date_in, timezone.get_default_timezone())
        xmltrack.save()


        vtrack_id = xmltrack.perform_id

        #SPC details (child)
        for paramElement in root.findall('spc/summary_result/parameter'):
            parameter = paramElement.attrib['name']
            param_result = paramElement.findtext('result')
            min_value = paramElement.findtext('min')
            max_value = paramElement.findtext('max')
            param_unit = paramElement.findtext('unit')
            lower_limit = paramElement.findtext('lowerlimit')
            upper_limit = paramElement.findtext('upperlimit')

            xmlDetail = PerformingDetail()
            xmlDetail.perform_id = xmltrack
            xmlDetail.param_name = parameter
            xmlDetail.result = True if param_result == 'P' else False
            xmlDetail.min_value = min_value
            xmlDetail.max_value = max_value
            xmlDetail.unit_name = param_unit
            xmlDetail.lower_limit = lower_limit
            xmlDetail.upper_limit = upper_limit
            xmlDetail.spc_required = xmlDetail.is_master_required()
            xmlDetail.datetime = xmltrack.datetime
            xmlDetail.save()
            if data_type == 'VALIDATE':
                xmlDetail.excecute_spc()

        if data_type == 'VALIDATE':
            #Update Perform Setting
            pd = PerformingDetail.objects.filter(perform_id=vtrack_id,spc_required=True,spc_result=False)
            ps = PerformSetting.objects.get(tester_name= testername)

            ps.last_perform_datetime = timezone.now()
            ps.last_perform_result = True if result == 'P' else False
            ps.perform_id = vtrack_id
            ps.last_spc_result = True if pd.count() == 0 else False
            #update action log. (if there is SPC failed, it requires Action log
            if pd.count() > 0 and ps.tester_name.control  :
                ps.require_actions = True
            ps.save()
            #End Update

        return "Successful"

    except Exception as e:
        return "Failed : Unable to insert transaction %s" % e.args[0]



@api_view(['GET', 'PUT', 'DELETE'])
def perform_tracking(request, year, month, day, type):
    """
    Get, udpate, or delete a specific task
    """
    try:
        testPerform = PerformingTracking.objects.filter(datetime__year= year,
                                                        datetime__month= month,
                                                        datetime__day= day,
                                                        type=type)
    except PerformingTracking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PerformTrakingSerializer(testPerform, many=True)
        return Response(serializer.data )

@api_view(['GET', 'PUT', 'DELETE'])
def perform_detail(request, perform_id):
    """
    Get, udpate, or delete a specific task
    """
    try:
        testPerformDetail = PerformingDetail.objects.filter(perform_id= perform_id)
    except PerformingDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PerformDetailSerializer(testPerformDetail, many=True)
        return Response(serializer.data )


@api_view(['GET'])
def perform_actions(request, perform_id):
    """
    Get, udpate, or delete a specific task
    """
    try:
        testPerformActions = PerformingActionLog.objects.filter(perform_id= perform_id)
    except testPerformActions.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PerformActionsSerializer(testPerformActions, many=True)
        return Response(serializer.data )

@api_view(['GET'])
def last_failed_spc(request, tester_name):
    """
    Get, udpate, or delete a specific task
    """
    try:
        ps = PerformSetting.objects.get(tester_name=tester_name)
        pd = PerformingDetail.objects.filter(perform_id=ps.perform_id,spc_required=True,spc_result=False)
    except PerformingDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PerformDetailSerializer(pd, many=True)
        return Response(serializer.data )


@api_view(['GET'])
def tester_ready(request, tester_name):
    try:
        qtestermaster = TesterMaster.objects.get(tester_name= tester_name)
        #return Response({'response': True})
        #check Overdue
        if not qtestermaster.is_on_due():
                return Response({'response': False ,'message':'Over due ,Need to run Golden unit'})
        #if spc_enable =False , do not check SPC status
        if qtestermaster.control :
            #{'response': False ,'message':'Over due , need to run Golden unit'}
            if not qtestermaster.is_spc_passed() :
                return Response({'response': False ,'message':'SPC failed!!'})
            elif qtestermaster.is_action_pending()  :
                return Response({'response': False ,'message':'Require actions for previous SPC failure'})
            else:
                return Response({'response': True})
        else:
            return Response({'response': True})
            #{'response': False ,'message':'SPC failed!!'}

    except Exception as e:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', 'POST'])
def perform_action_update(request, perform_id, param_name, action_details):
    if request.method == 'PUT':
        q = PerformingDetail.objects.get (perform_id=perform_id,
                                          param_name=param_name)
        q.action_details = action_details
        q.save()
        return Response("Successful")



@api_view(['GET', 'PUT', 'DELETE'])
def param_setting_detail(request):
    """
    Retrieve, update or delete a snippet instance.
    """
    #try:
    #    snippet = Snippet.objects.get(pk=pk)
    #except Snippet.DoesNotExist:
    #    return Response(status=status.HTTP_404_NOT_FOUND)

    #if request.method == 'GET':
    #    serializer = SnippetSerializer(snippet)
    #    return Response(serializer.data)

    if request.method == 'GET':
        settingDetail = ParamSetting.objects.all()
        serializer = ParamSettingSerializer(settingDetail, many=True)
        return Response(serializer.data )

    if request.method == 'PUT':
        if True :
            xml = request.body
            return Response(add_paramSetting(xml))
        else:
            return Response("Accept only xml (ODC/SPC compatible)" )
        #import json
        #obj_generator=json.dumps(request.data)
        #serializer = ParamSettingSerializer(data=obj_generator)
        #if serializer.is_valid(serializer):
        #    return Response("Setting API - Validate Done")
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def add_paramSetting(xml):
    try:
        root = ET.fromstring(xml)
        #Main data
        tester_name = root.findtext('tester_name')
        param_name = root.findtext('param_name')
        model = root.findtext('model')
        ucl2s = root.findtext('ucl2s')
        ucl1s = root.findtext('ucl1s')
        ucl = root.findtext('ucl')
        cl = root.findtext('cl')
        lcl2s = root.findtext('lcl2s')
        lcl1s = root.findtext('lcl1s')
        lcl = root.findtext('lcl')
        control_side = root.findtext('control_side')

        xmlParamSetting = ParamSetting()
        xmlParamSetting.tester_name = TesterMaster.objects.get(tester_name=tester_name)
        xmlParamSetting.param_name= ParamMaster.objects.get(param_name=param_name)
        xmlParamSetting.model=model
        xmlParamSetting.ucl2s=ucl2s
        xmlParamSetting.ucl1s=ucl1s
        xmlParamSetting.ucl=ucl
        xmlParamSetting.cl=cl
        xmlParamSetting.lcl2s=lcl2s
        xmlParamSetting.lcl1s=lcl1s
        xmlParamSetting.lcl=lcl
        xmlParamSetting.control_side=control_side
        xmlParamSetting.active = True
        xmlParamSetting.save()

        return ("Successful")

    except Exception as e:
        return ("Failed : Unable to insert Parameter Setting")


