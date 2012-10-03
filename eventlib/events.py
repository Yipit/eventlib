from eventlib import BaseEvent, external_handler, handler


class ViewedDeals(BaseEvent):
    def broadcast(self, data):
        data['tester'] = 'extra'
        return data


@external_handler('eventlib.ViewedDeals')
def redis_log(data):
    print "external", data


@handler('eventlib.ViewedDeals')
def redis_log2(data):
    print "internal", data
