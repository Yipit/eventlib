from mock import Mock

from eventlib import conf, util


def test_overriding_get_ip_helper_config():
    # Given I overrided the local geolocation config
    conf.LOCAL_GEOLOCATION_IP = 'my geolocation ip'

    # When I call the get_ip function, then it should return the
    # overrided value
    util.get_ip(None).should.equal('my geolocation ip')

    # Cleaning up
    conf.LOCAL_GEOLOCATION_IP = ''


def test_geo_ip_helper_with_an_unknown_ip():
    # Given I have a request object with the `HTTP_X_FORWARDED_FOR`
    # variable set to a false value
    request = Mock()
    request.META = {'HTTP_X_FORWARDED_FOR': ''}

    # When I call the get_ip helper, it should return a default
    # 'unknown' value
    util.get_ip(request).should.equal('0.0.0.0')


def test_get_ip_helper():
    # Given I have a request object with the `HTTP_X_FORWARDED_FOR`
    # variable set with local and remote IP addresses
    request = Mock()
    request.META = {
        'HTTP_X_FORWARDED_FOR': '127.0.0.1,10.0.0.1,150.164.211.1'}

    # When I call the get_ip helper, it should skip the local addresses
    # and give me the first remote address
    util.get_ip(request).should.equal('150.164.211.1')

    # If the request only contain local addresses, the output should be
    # the default unknown addr
    request.META = {
        'HTTP_X_FORWARDED_FOR': '127.0.0.1,10.0.0.1,10.1.1.25'}
    util.get_ip(request).should.equal('0.0.0.0')
