from django import template

register = template.Library()


@register.simple_tag(name='cpu')
def cpu(usl,avg,std):
    return 0 if std == 0 else (usl-avg)/(3*std)


@register.simple_tag(name='cpl')
def cpl(lsl,avg,std):
    return 0 if std == 0 else (avg-lsl)/(3*std)


@register.simple_tag(name='cpk')
def cpk(lsl,usl,avg,std):
    if std == 0:
        z= 0
    else:
        x = (avg-lsl)/(3*std)
        y = (usl-avg)/(3*std)
        z = x if x < y else y
    return z


@register.simple_tag(name='cp')
def cp(lsl,usl,std):
    if std == 0:
        y = 0
    else:
        y = (usl-lsl)/(6*std)
    return y
