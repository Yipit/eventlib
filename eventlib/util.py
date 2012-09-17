from . import conf

UNKNOWN_IP = '0.0.0.0'


def get_ip(request):
    if conf.LOCAL_GEOLOCATION_IP:
        return conf.LOCAL_GEOLOCATION_IP

    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if not forwarded_for:
        return UNKNOWN_IP

    for ip in forwarded_for.split(','):
        ip = ip.strip()
        if not ip.startswith('10.') and not ip == '127.0.0.1':
            return ip

    return UNKNOWN_IP
