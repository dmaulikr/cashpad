import copy
import simplejson
import datetime

import grok
from zope.location.location import located
from zope.formlib.form import applyData
from zope.publisher.interfaces import BadRequest

from cashpad.interfaces import IOrder, IItem
from cashpad.models import Orders, Order, Users, User, Item

class APILayer(grok.IRESTLayer):
    grok.restskin('api')

# XXX PUT requests in grok don't work like you would expect them to?
class UsersTraverser(grok.Traverser):
    grok.context(Users)
    grok.layer(APILayer)

    def traverse(self, name):
        if self.request.method == 'PUT':
            response = self.request.response
            user = self.context.get(name)
            if user is None:
                user = self.context[name] = User()
                response.setStatus('201')
            else:
                response.setStatus('204')

            # FIXME: user should not be a hardcoded string like this
            location = located(self.context, self.context.__parent__, self.context.__name__)
            return location

class UsersREST(grok.REST):
    grok.context(Users)
    grok.layer(APILayer)

    def PUT(self):
        # XXX We/grok should set the location here.
        return ''

class OrdersREST(grok.REST):
    grok.context(Orders)
    grok.layer(APILayer)

    def validate_proper_contenttype(self):
        if  self.request.getHeader('Content-Type', '').lower() != 'application/json; charset=utf-8':
            raise BadRequest('Content is not of type: application/json; charset=utf-8')

    def parse_json(self):
        "Return parsed json, otherwise raise BadRequest"
        try:
            parsed_body = simplejson.loads(self.body)
        except ValueError:
            raise BadRequest('Content could not be parsed')
        
        return parsed_body

    def coerce_order_data(self, original_order_data):
        order_data = copy.deepcopy(original_order_data)
        
        # Coerce the created_on timestamp to a datetime
        order_data['created_on'] = datetime.datetime.fromtimestamp(order_data['created_on'])
        # Coerce total_price to float
        order_data['total_price'] = float(order_data['total_price'])

        return order_data

    def coerce_item_data(self, original_item_data):
        item_data = copy.deepcopy(original_item_data)
        
        # Coerce unit_price to float
        item_data['unit_price'] = float(item_data['unit_price'])
        
        return item_data

    def POST(self):
        self.validate_proper_contenttype()

        order_data = self.parse_json()
        order_data = self.coerce_order_data(order_data)

        item_list = []
        for item_data in order_data['item_list']:
            item_data = self.coerce_item_data(item_data)
            
            item = Item()
            applyData(item, grok.Fields(IItem), item_data)
            item_list.append(item)

        order_data['item_list'] = item_list
        
        order = Order()
        applyData(order, grok.Fields(IOrder), order_data)
        
        self.context.add(order)

        self.response.setHeader('Location', self.url(order))
        self.response.setStatus('201')
        return ''

