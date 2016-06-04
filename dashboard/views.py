from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from spc.models import TesterMaster
from spc.models import PerformingDetail
from spc.models import PerformingTracking
from spc.models import PerformExecute
from spc.models import PerformingActionLog
from spc.models import PerformSetting
from spc.models import ParamSetting

from django.utils import timezone

import ast
from .forms import ActionForm
from .forms import UnitTrackingForm
from .forms import OperationForm

from django.contrib.auth.decorators import login_required




def index(request):
    latest_tester_list = TesterMaster.objects.order_by('group')
    template = loader.get_template('dashboard/index.html')
    context = RequestContext(request, {
        'latest_tester_list': latest_tester_list,
    })
    return HttpResponse(template.render(context))


def unittrack(request):
    latest_tester_list = TesterMaster.objects.order_by('group')
    template = loader.get_template('dashboard/unit_tracking.html')
    context = RequestContext(request, {
        'latest_tester_list': latest_tester_list,
    })
    return HttpResponse(template.render(context))


def operationQuery(request):
    template = loader.get_template('dashboard/operationQuery.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


def view_perform_detail(request,perform_id,perform_type):
    perform_detail_list = PerformingDetail.objects.filter(perform_id=perform_id,spc_required=True).order_by('-spc_required')

    if perform_detail_list.count() > 0 :
        tester_name = perform_detail_list[0].perform_id.tester_name
        gu_sn = perform_detail_list[0].perform_id.sn
    else:
        pt = PerformingTracking.objects.get(perform_id=perform_id)
        tester_name = pt.tester_name
        gu_sn = pt.sn
    #modify by Chutchai on Jan 6,2016
    #To filter only VALIDATE
    perform_tracking_list = PerformingTracking.objects.filter(tester_name=tester_name,
                                                              type=perform_type).order_by('-datetime')[:10]

    gu_tracking_list = PerformingDetail.objects.filter(perform_id__sn=gu_sn,
                                                       spc_required=True,perform_id__type=perform_type).order_by('-datetime')[:20]

    template = loader.get_template('dashboard/perform_detail.html')
    context = RequestContext(request, {
        'perform_detail_list': perform_detail_list,
        'perform_tracking_list' : perform_tracking_list,
        'gu_tracking_list' : gu_tracking_list,
    })
    return HttpResponse(template.render(context))


def view_param_detail(request,tester_name,param_name,rule_name,side,perform_type):
    perform_param_detail_list = PerformExecute.objects.filter(side=side,rule_name_id=rule_name,
                                  perform_param__param_name=param_name,
                                  perform_param__perform_id__tester_name=tester_name,
                                  perform_param__perform_id__type=perform_type).order_by('-perform_param__datetime')

    template = loader.get_template('dashboard/perform_param_detail.html')
    context = RequestContext(request, {
        'perform_param_detail_list': perform_param_detail_list
    })
    return HttpResponse(template.render(context))


def view_chart_detail(request,tester_name,param_name,perform_type):
    perform_detail_list = PerformingDetail.objects.filter(param_name=param_name,
                                                          perform_id__tester_name=tester_name,
                                                          perform_id__type=perform_type).order_by('-perform_id__datetime')[:50]

    param_setting_list = ParamSetting.objects.filter(param_name=param_name, tester_name=tester_name,active=True)

    template = loader.get_template('dashboard/perform_chart_detail.html')
    context = RequestContext(request, {
        'perform_detail_list': perform_detail_list,
        'param_setting_list' : param_setting_list
    })
    return HttpResponse(template.render(context))


#@login_required
def set_actions(request, perform_id):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ActionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            actions = form.cleaned_data['action_text']
            #Update PerformDetails (perform_id)
            pt = PerformingTracking.objects.get(perform_id=perform_id)
            pa = PerformingActionLog()
            pa.perform_id = pt
            pa.tester_name = pt.tester_name
            pa.datetime = timezone.now()
            pa.result = False
            pa.action_details = actions
            pa.save()

            #Update PerformSetting
            ps = PerformSetting.objects.get(tester_name=pt.tester_name)
            if actions != "":
                ps.require_actions = False
                ps.save()

            #message = form.cleaned_data['message']
            #sender = form.cleaned_data['sender']
            #cc_myself = form.cleaned_data['cc_myself']
            # redirect to a new URL:

            #return HttpResponseRedirect('/dashboard/%s/' % perform_id)
            return HttpResponseRedirect('/dashboard/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ActionForm()

    return render(request, '../templates/dashboard/actions.html', {'form': form ,
                                                'perform_id' : perform_id})


def form_unit_tracking(request):
    # if this is a POST request we need to process the form data
    pt = PerformingTracking()

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UnitTrackingForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            unit_sn = form.cleaned_data['unit_text']
            #Update PerformDetails (perform_id)
            pt = PerformingTracking.objects.filter(sn=unit_sn , type='PROD')
        else :
            pt = None
            #pa = PerformingActionLog()
            #pa.perform_id = pt
            #pa.tester_name = pt.tester_name
            #pa.datetime = timezone.now()
            #pa.result = False
            #pa.action_details = actions
            #pa.save()

            #Update PerformSetting
            #ps = PerformSetting.objects.get(tester_name=pt.tester_name)
            #if unit_sn != "":
            #    ps.require_actions = False
            #    ps.save()

            #message = form.cleaned_data['message']
            #sender = form.cleaned_data['sender']
            #cc_myself = form.cleaned_data['cc_myself']
            # redirect to a new URL:

            #return HttpResponseRedirect('/dashboard/%s/' % perform_id)
            #return HttpResponseRedirect('/dashboard/unit_track/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UnitTrackingForm()
        pt = None

        #return render(request, '../templates/dashboard/unit_tracking.html', {'form': form})

    return render(request, '../templates/dashboard/unit_tracking.html', {'form': form, 'performtracking':pt})


def view_query_oper_model(request,operation_name,model_name,
                          date_from_in,date_to_in,group_by,parameter,tester):
    import datetime
    #date_object2=date_from.strftime('%d/%m/%Y %H:%M:%S')
    date_from = datetime.datetime.strptime(date_from_in, '%d-%m-%Y %H:%M:%S')
    date_to = datetime.datetime.strptime(date_to_in, '%d-%m-%Y %H:%M:%S')

    from django.db.models import Count,Max,Min,Avg,StdDev

    g1 = 'perform_id__tester_name'
    g2 = 'param_name'

    if group_by == 'TESTER':
        g1 = 'perform_id__tester_name'
        g2 = 'param_name'

    if group_by == 'PARAMETER':
        g1 = 'param_name'
        g2 = 'perform_id__tester_name'

    pt = PerformingDetail.objects.filter(perform_id__datetime__gt=datetime.datetime(date_from.year,
                                                                                    date_from.month,
                                                                                    date_from.day),
                                         perform_id__datetime__lt=datetime.datetime(date_to.year,
                                                                                    date_to.month,
                                                                                    date_to.day),
                                         perform_id__station=operation_name,
                                         perform_id__model=model_name)\
        .exclude(max_value=9999).values(g1,g2)\
        .annotate(total=Count('max_value'),min=Min('max_value'),
                  max=Max('max_value'),avg=Avg('max_value'),std=StdDev('max_value'),
                  limit_min=Max('lower_limit'),limit_max=Max('upper_limit'))\
        .order_by(g1,g2)

    if group_by == 'PARAMETER':
        if parameter != 'ALL':
            pt = pt.filter(param_name=parameter)

    if group_by == 'TESTER':
        if tester != 'ALL':
            pt = pt.filter(perform_id__tester_name=tester)




    template = loader.get_template('dashboard/query_cpk_operation.html')
    context = RequestContext(request, {
        'spcdetails':pt ,
        'startdate':date_from_in,
        'enddate':date_to_in,
        'operation':operation_name,
        'model': model_name,
        'group_by':group_by,
        'parameter':parameter,
        'tester':tester})
    return HttpResponse(template.render(context))


def view_query_oper_main(request,operation_name,
                          date_from_in,date_to_in):
    import datetime
    date_from = datetime.datetime.strptime(date_from_in, '%d-%m-%Y %H:%M:%S')
    date_to = datetime.datetime.strptime(date_to_in, '%d-%m-%Y %H:%M:%S')

    from django.db.models import Count,Max,Min,Avg,StdDev
    pt = PerformingDetail.objects.filter(perform_id__datetime__gt=datetime.datetime(date_from.year,
                                                                                    date_from.month,
                                                                                    date_from.day),
                                         perform_id__datetime__lt=datetime.datetime(date_to.year,
                                                                                    date_to.month,
                                                                                    date_to.day),
                                         perform_id__station=operation_name)\
        .exclude(max_value=9999).values('perform_id__model','param_name')\
        .annotate(total=Count('max_value'),min=Min('max_value'),
                  max=Max('max_value'),avg=Avg('max_value'),std=StdDev('max_value'),
                  limit_min=Max('lower_limit'),limit_max=Max('upper_limit'))\
        .order_by('perform_id__model','param_name')

    template = loader.get_template('dashboard/query_by_operation.html')
    context = RequestContext(request, {
        'spcdetails':pt ,
        'startdate':date_from_in,
        'enddate':date_to_in,
        'operation':operation_name})
    return HttpResponse(template.render(context))



def form_oper_query(request):
    # if this is a POST request we need to process the form data
    pt = PerformingDetail()
    date_object_from=None
    date_object_to=None

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = OperationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            date_from = form.cleaned_data['start_date']
            date_to = form.cleaned_data['end_date']
            operation = form.cleaned_data['operation']

            import datetime

            date_object_from=date_from.strftime('%d-%m-%Y %H:%M:%S')
            date_object_to=date_to.strftime('%d-%m-%Y %H:%M:%S')
            #date_object = datetime.datetime.strptime(date_object_from, '%d/%m/%Y %H:%M:%S')

            from django.db.models import Count,Max,Min,Avg,StdDev
            pt = PerformingDetail.objects.filter(perform_id__datetime__gt=datetime.datetime(date_from.year,
                                                                                            date_from.month,
                                                                                            date_from.day),
                                                 perform_id__datetime__lt=datetime.datetime(date_to.year,
                                                                                            date_to.month,
                                                                                            date_to.day),
                                                 perform_id__station=operation)\
                .exclude(max_value=9999).values('perform_id__model','param_name')\
                .annotate(total=Count('max_value'),min=Min('max_value'),
                          max=Max('max_value'),avg=Avg('max_value'),std=StdDev('max_value'),
                          limit_min=Max('lower_limit'),limit_max=Max('upper_limit'))\
                .order_by('perform_id__model','param_name')
            #pt = None
        else :
            pt = None
            date_from =''
            date_to =''
            operation=''
            #date_object2=''
            #date_object=None
            #pa = PerformingActionLog()
            #pa.perform_id = pt
            #pa.tester_name = pt.tester_name
            #pa.datetime = timezone.now()
            #pa.result = False
            #pa.action_details = actions
            #pa.save()

            #Update PerformSetting
            #ps = PerformSetting.objects.get(tester_name=pt.tester_name)
            #if unit_sn != "":
            #    ps.require_actions = False
            #    ps.save()

            #message = form.cleaned_data['message']
            #sender = form.cleaned_data['sender']
            #cc_myself = form.cleaned_data['cc_myself']
            # redirect to a new URL:

            #return HttpResponseRedirect('/dashboard/%s/' % perform_id)
            #return HttpResponseRedirect('/dashboard/unit_track/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = OperationForm()
        pt = None
        date_from =''
        date_to =''
        operation=''
        #date_object=None
        #date_object2=''


        #return render(request, '../templates/dashboard/unit_tracking.html', {'form': form})

    return render(request, '../templates/dashboard/operationQuery.html', {'form': form, 'spcdetails':pt ,
                                                                          'startdate':date_object_from,
                                                                          'enddate':date_object_to,
                                                                          'operation':operation})


def example_plot(ax):
    ax.plot([1, 2])
    ax.set_xlabel('x-label')
    ax.set_ylabel('y-label')
    ax.set_title('Title')


def box_plot(ax,data,title=''):
    #import numpy as np
    #np.random.seed(937)
    #data = np.random.lognormal(size=(37, 4), mean=1.5, sigma=1.75)
    #labels = list('ABCD')
    ax.boxplot(data, 0, 'gD', 0)#rs
    #(data, 0, 'rs', 0,meanline=True, showmeans=True)
    #ax.set_xlabel('x-label')
    #ax.set_ylabel('y-label')
    ax.set_title(title)


def histogram(ax,datas,operation_name,model_name,
                          date_from_in,date_to_in,group_by,parameter,tester):
    import matplotlib.mlab as mlab

    #Query data
    #import datetime
    from django.db.models import Count,Max,Min,Avg,StdDev

    #get Aggregate data


    means = datas.aggregate(mean=Avg('max_value')).get('mean')
    stddev = datas.aggregate(stddev=StdDev('max_value')).get('stddev')


    x = list(datas.values_list('max_value', flat=True))
    x.remove(max(x))
    limit_min = datas.aggregate(min=Min('lower_limit')).get('min')
    limit_max = datas.aggregate(max=Min('upper_limit')).get('max')

    #mylist = list(pt.filter(perform_id__tester_name=tester).values_list('max_value',flat=True))
    #mylist.remove(max(mylist))
    # example data
    mu = means #100  # mean of distribution
    sigma = stddev #15  # standard deviation of distribution

    #ax.set_xlabel('%s on %s of %s' % (parameter,tester,model_name))
    #ax.set_ylabel('Probability')
    ax.set_title(r'Histogram of %s : $\mu = %0.2f $, $\sigma=%0.2f$' % (model_name,means,stddev))

    if sigma != 0:
        num_bins = 100 if datas.count()>100 else datas.count()
        # the histogram of the data
        n, bins, patches = ax.hist(x, num_bins, normed=1, facecolor='green', alpha=0.7)
        # add a 'best fit' line
        y = mlab.normpdf(bins, mu, sigma)
        #ax.set_xlim(limit_min,limit_max)
        #ax.set_ylim(0,0.1)
        ax.plot(bins, y, 'r--')

        #Line limit min/max
        # draw a default vline at x=1 that spans the yrange
        l = ax.axvline(x=limit_min)
        ax.text(limit_min,max(y),limit_min, ha='left',
                verticalalignment='bottom',color='black', wrap=True,
                bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

        l = ax.axvline(x=limit_max)
        ax.text(limit_max,max(y),limit_max, ha='left',
                verticalalignment='bottom',color='black', wrap=True,
                bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})


def graphsviewbar(request,tester_name,param_name,model,side):
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt
    import numpy as np

    fig = plt.Figure()
    ax = fig.add_subplot(211) #211 ,111
    ay = fig.add_subplot(212)
    #fig.tight_layout()
    fig.tight_layout(pad=2, w_pad=0.5, h_pad=4.0)
    #get limit
    from spc.models import ParamSetting
    ps = ParamSetting.objects.get(tester_name=tester_name,param_name=param_name,
                                 model=model,control_side=side)
    titletxt= 'IR chart : %s - %s (%s)' % (tester_name,param_name,side)

    pd = PerformingDetail.objects.filter(param_name=param_name,
                                         perform_id__tester_name=tester_name).order_by('-datetime')[:50]

    minvalue_list = pd.values_list('min_value', flat=True)[::-1]
    maxvalue_list = pd.values_list('max_value', flat=True)[::-1]
    date_list = pd.values_list('datetime', flat=True)[::-1]



    n = pd.count()
    cl = np.empty(n)
    ucl = np.empty(n)
    ucl1s = np.empty(n)
    ucl2s = np.empty(n)
    lcl = np.empty(n)
    lcl1s = np.empty(n)
    lcl2s = np.empty(n)

    cl.fill(ps.cl)
    ucl.fill(ps.ucl)
    lcl.fill(ps.lcl)
    ucl1s.fill(ps.ucl1s)
    lcl1s.fill(ps.lcl1s)
    ucl2s.fill(ps.ucl2s)
    lcl2s.fill(ps.lcl2s)

    #x=np.arange(1,n+1)
    #ax.set_xlim(1, 50)
    dim = np.arange(0, n+1)
    x=np.arange(1,n+1)
    #x=date_list
    #y = np.full(n, 1)
    #y = np.full(n, ps.lcl*0.6)
    y = minvalue_list if side == 'MIN' else maxvalue_list

    box_plot(ay,y ,'')

    #Center Line (CL)
    ax.plot(x,cl,linestyle='-',color='black', linewidth=2)
    ax.text(1, ps.cl,ps.cl.__format__('0.3'), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'gray', 'alpha':0.5, 'pad':1})

    #1Sigma Upper line (1ucl)
    ax.plot(x,ucl1s,linestyle='--',color='green', linewidth=1)
    ax.text(1, ps.ucl1s,ps.ucl1s.__format__('0.3'), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'green', 'alpha':0.5, 'pad':1})

    #1Sigma Lower line (1lcl)
    ax.plot(x,lcl1s,linestyle='--',color='green', linewidth=1)
    ax.text(1, ps.lcl1s,ps.lcl1s.__format__('0.3'), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'green', 'alpha':0.5, 'pad':1})

    #2Sigma Upper line (2ucl)
    ax.plot(x,ucl2s,linestyle='--',color='orange', linewidth=1)
    ax.text(1, ps.ucl2s,ps.ucl2s.__format__('0.3'), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'orange', 'alpha':0.5, 'pad':1})

    #2Sigma Upper line (2lcl)
    ax.plot(x,lcl2s,linestyle='--',color='orange', linewidth=1)
    ax.text(1, ps.lcl2s,ps.lcl2s.__format__('0.3'), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'orange', 'alpha':0.5, 'pad':1})

    #3Sigma Upper line (3ucl)
    ax.plot(x,ucl,linestyle='-',color='red', linewidth=2)
    ax.text(1, ps.ucl,ps.ucl.__format__('0.3'), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    #3Sigma lower line (3lcl)
    ax.plot(x,lcl,linestyle='-',color='red', linewidth=2)
    ax.text(1, ps.lcl,ps.lcl.__format__('0.3'), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    #xlabels = [newdate.strftime('%b-%d %I:%M %p') if True else newdate for newdate in date_list]#'%b-%d'
    from django.utils import timezone
    xlabels = [timezone.localtime(newdate, timezone.get_default_timezone()).strftime('%b-%d') if True else newdate for newdate in date_list]#'%b-%d'

    from matplotlib.ticker import MultipleLocator, FormatStrFormatter
    majorLocator   = MultipleLocator(1)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator   = MultipleLocator(1)
    minorFormatter = FormatStrFormatter('%d')

    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.xaxis.set_major_formatter(minorFormatter)

    ax.plot(x,y,'o-')
    #fig.xticks(dim)
    #fig.grid()
    #ax.set_xticks(date_list)
    labels = ['0','a', 'b', 'c', 'd','e','f','g','h','i','j','k','l',
              'm','n','o','p','q','r','s','t','u','v','w','x','y','z',
              'a1', 'b2', 'c3', 'd4','e5','f6','g7','h8','i9','j10','k11','l12',
              'm13','n14','o15','p16','q17','r18','s19','t20','u21','v22','w23','x24']
    labels=['0']+xlabels
    ax.set_xticklabels(labels, rotation=70,ha='right')

    #for label in ax.get_xticklabels():
    #    label.set_rotation('vertical')


    #ax.plot(r.date, r.close)

    # rotate and align the tick labels so they look better
    #fig.autofmt_xdate()

    # use a more precise date string for the x axis locations in the
    # toolbar
    #plt.title('fig.autofmt_xdate fixes the labels')

    ax.set_title(titletxt)



    #ax.set_xticks(date_list)

    #ax.set_xticks(date_list)
    #ax.set_xticklabels(xlable , rotation=45) #Working but need to fix format

    #ax.set_xticklabels(date_list)
    #ax.set_minor_formatter(FormatStrFormatter("%b"))
    ax.set_ylim([(ps.lcl+(ps.lcl1s-ps.cl)), (ps.ucl+(ps.ucl1s-ps.cl))])


    ax.xaxis.grid(True,'major',linewidth=1)
    ax.tick_params(axis='x', pad=8)
    #ax.xaxis.grid(True,'minor')
    #fig.tight_layout()

    #fig.autofmt_xdate()
    # rotate and align the tick labels so they look better
    #fig.autofmt_xdate()

# use a more precise date string for the x axis locations in the
# toolbar

    #plt.title('fig.autofmt_xdate fixes the labels')
    #ax.imshow(X, cmap=cm.jet)

    fig.set_size_inches(13,8, forward=True)
    #plt.savefig("image.png",bbox_inches='tight',dpi=100)
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def graph_histogram(request,operation_name,model_name,
                          date_from_in,date_to_in,group_by,parameter,tester):
    import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt


    #Query data
    import datetime
    from django.db.models import Count,Max,Min,Avg,StdDev
    date_from = datetime.datetime.strptime(date_from_in, '%d-%m-%Y %H:%M:%S')
    date_to = datetime.datetime.strptime(date_to_in, '%d-%m-%Y %H:%M:%S')

    pt = PerformingDetail.objects.filter(perform_id__datetime__gt=datetime.datetime(date_from.year,
                                                                                    date_from.month,
                                                                                    date_from.day),
                                         perform_id__datetime__lt=datetime.datetime(date_to.year,
                                                                                    date_to.month,
                                                                                    date_to.day),
                                         perform_id__station=operation_name,
                                         perform_id__model=model_name,
                                         perform_id__tester_name=tester,
                                         param_name=parameter)\
        .exclude(max_value=9999)
    #get Aggregate data
    means = pt.aggregate(mean=Avg('max_value')).get('mean')
    stddev = pt.aggregate(stddev=StdDev('max_value')).get('stddev')
    x = pt.values_list('max_value', flat=True)


    #limit_min = pt.aggregate(min=Min('lower_limit')).get('min')
    #limit_max = pt.aggregate(max=Min('upper_limit')).get('max')

    limit_min = pt.aggregate(min=Max('lower_limit')).get('min')
    limit_max = pt.aggregate(max=Min('upper_limit')).get('max')

    fig = plt.Figure()
    ax = fig.add_subplot(211) #211 ,111
    ay = fig.add_subplot(212)

    box_plot(ay,x,'')
    # example data
    mu = means #100  # mean of distribution
    sigma = stddev #15  # standard deviation of distribution
    #x = mu + sigma * np.random.randn(10000)

    num_bins = 100 if pt.count()>100 else pt.count()
    # the histogram of the data
    n, bins, patches = ax.hist(x, num_bins, normed=1, facecolor='green', alpha=0.7)
    # add a 'best fit' line
    y = mlab.normpdf(bins, mu, sigma)

    #ax.plot(x,cl,linestyle='-',color='black', linewidth=2)

    #ax.set_xlim(limit_min,limit_max)

    ax.plot(bins, y, 'r--')
    #ax.set_xlabel('%s on %s' % (parameter,tester))
    ax.set_ylabel('Probability')
    ax.set_title(r'Histogram of %s : $\mu = %0.2f $, $\sigma=%0.2f$' % (parameter,means,stddev))
    ax.set_xlabel('model: %s  / tester: %s' % (model_name,tester))
    # Tweak spacing to prevent clipping of ylabel
    #plt.subplots_adjust(left=0.15)
    #ax.set_subplots_adjust(left=0.15)
    #fig.set_size_inches(13,8, forward=True)

    #Line limit min/max
    # draw a default vline at x=1 that spans the yrange
    l = ax.axvline(x=limit_min)
    ax.text(limit_min,max(y),limit_min, ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    l = ax.axvline(x=limit_max)
    ax.text(limit_max,max(y),limit_max, ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    #fig.set_size_inches(13,8, forward=True)
    fig.tight_layout()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def graph_boxplot(request,operation_name,model_name,
                          date_from_in,date_to_in,group_by,parameter,tester):
    import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt


    #Query data
    import datetime
    from django.db.models import Count,Max,Min,Avg,StdDev
    date_from = datetime.datetime.strptime(date_from_in, '%d-%m-%Y %H:%M:%S')
    date_to = datetime.datetime.strptime(date_to_in, '%d-%m-%Y %H:%M:%S')

    pt = PerformingDetail.objects.filter(perform_id__datetime__gt=datetime.datetime(date_from.year,
                                                                                    date_from.month,
                                                                                    date_from.day),
                                         perform_id__datetime__lt=datetime.datetime(date_to.year,
                                                                                    date_to.month,
                                                                                    date_to.day),
                                         perform_id__station=operation_name,
                                         perform_id__model=model_name,
                                         param_name=parameter)\
        .exclude(max_value=9999)

    labels = pt.distinct('perform_id__tester_name').values_list('perform_id__tester_name',flat=True)

    x_data=[]
    for tester in pt.distinct('perform_id__tester_name').values_list('perform_id__tester_name',flat=True):
        mylist = list(pt.filter(perform_id__tester_name=tester).values_list('max_value',flat=True))
        mylist.remove(max(mylist))
        x_data.append(mylist)

    adjustprops = dict(left=0.1, bottom=0.1, right=0.97, top=0.93, wspace=1, hspace=1)

    fig = plt.Figure()
    fig.suptitle('Box plot of %s  (all tester)' % parameter , fontsize=14, fontweight='bold')
    fig.subplots_adjust(**adjustprops)
    ax = fig.add_subplot(111) #211 ,111
    ax.boxplot(x_data,labels=labels)#rs
    ax.set_xticklabels( labels, rotation=80,ha='right')
    #ax.set_title(r'Parameter : %s' % (parameter))
    ax.set_xlabel('model: %s  / operation: %s' % (model_name,operation_name))
    #fig.set_size_inches(13,8, forward=True)
    fig.tight_layout()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def graph_hist_all_model(request,operation_name,model_name,
                          date_from_in,date_to_in,group_by,parameter,tester):
    import numpy as np
    import matplotlib.mlab as mlab
    #import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    #from matplotlib import pyplot as plt
    import matplotlib.pyplot as plt


    #Query data
    import datetime
    date_from = datetime.datetime.strptime(date_from_in, '%d-%m-%Y %H:%M:%S')
    date_to = datetime.datetime.strptime(date_to_in, '%d-%m-%Y %H:%M:%S')

    pt = PerformingDetail.objects.filter(perform_id__datetime__gt=datetime.datetime(date_from.year,
                                                                                    date_from.month,
                                                                                    date_from.day),
                                         perform_id__datetime__lt=datetime.datetime(date_to.year,
                                                                                    date_to.month,
                                                                                    date_to.day),
                                         perform_id__station=operation_name,
                                         param_name=parameter)\
        .exclude(max_value=9999)

    #labels = pt.distinct('perform_id__tester_name').values_list('perform_id__tester_name',flat=True)
    rows = pt.distinct('perform_id__model').count()

    figprops = dict(figsize=(8., 8. / 1.618), dpi=128)                                          # Figure properties
    adjustprops = dict(left=0.1, bottom=0.1, right=0.97, top=0.93, wspace=1, hspace=1)
    plt.close('all')
    fig = plt.Figure()
    fig.suptitle('Histogram of %s  (all model)' % parameter , fontsize=14, fontweight='bold')
    fig.subplots_adjust(**adjustprops)
    model_data=[]
    loop=1

    from django.db.models import StdDev
    for model in pt.distinct('perform_id__model').values_list('perform_id__model',flat=True):
        mylist = pt.filter(perform_id__model=model).values_list('max_value',flat=True)
        stddev = mylist.aggregate(stddev=StdDev('max_value')).get('stddev')
        #Start to plot
        ax = fig.add_subplot(rows, 1,loop)
        #ax = plt.subplot2grid((rows, 1), (loop, 0), colspan=1)
        histogram(ax,mylist,operation_name,model,date_from,date_to,group_by,parameter,tester)
        loop = loop+1

        #ax = plt.subplot2grid((3, 6), (0, 0), colspan=6)

    fig.set_size_inches(10,12, forward=True)
    #fig.tight_layout()
    #fig.tight_layout()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response



#from spc.models import OperationMaster
#from spc.models import ParamMaster
#from django.shortcuts import render_to_response
#from django.http import HttpResponseBadRequest, JsonResponse
#from django.template import RequestContext
#import django_excel as excel
#import pyexcel.ext.xls
#import pyexcel.ext.xlsx
#import pyexcel.ext.ods3


#def export_data(request, operation_name,model_name,
#                          date_from_in,date_to_in,group_by,parameter):
#    import datetime
#    #date_object2=date_from.strftime('%d/%m/%Y %H:%M:%S')
#    date_from = datetime.datetime.strptime(date_from_in, '%d-%m-%Y %H:%M:%S')
#    date_to = datetime.datetime.strptime(date_to_in, '%d-%m-%Y %H:%M:%S')
#
#    from django.db.models import Count,Max,Min,Avg,StdDev
#
#    g1 = 'perform_id__tester_name'
#    g2 = 'param_name'
#
#    if group_by == 'TESTER':
#        g1 = 'perform_id__tester_name'
#        g2 = 'param_name'

#    if group_by == 'PARAMETER':
#        g1 = 'param_name'
#        g2 = 'perform_id__tester_name'
#   pt = PerformingDetail.objects.filter(perform_id__datetime__gt=datetime.datetime(date_from.year,
#                                                                                    date_from.month,
#                                                                                    date_from.day),
#                                         perform_id__datetime__lt=datetime.datetime(date_to.year,
#                                                                                    date_to.month,
#                                                                                    date_to.day),
#                                         perform_id__station=operation_name,
#                                         perform_id__model=model_name)


    #return excel.make_response_from_a_table(OperationMaster, 'xls', file_name="sheet")
    #elif report_type == "custom":
    #question = Question.objects.get(slug='ide')
#    query_sets = pt.values('perform_id__model','param_name','datetime')
#    column_names = ['perform_id__model','datetime','param_name']
#    return excel.make_response_from_query_sets(query_sets,column_names,'xls',file_name="custom")
    #else:
    #    return HttpResponseBadRequest("Bad request. please put one of these \
    #                                  in your url suffix: sheet, book or custom")
