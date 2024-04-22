from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
import json

class RequestMiddle(MiddlewareMixin):
    def process_request(self, request:HttpRequest):
        request.bodyJson = {}
        if request.body:
            request.bodyJson = json.loads(request.body.decode())
    

    def process_response(self, request:HttpRequest, response):
        # print(request)
        # if request.method == "OPTIONS":
        #     response['Access-Control-Allow-Origin'] = '*'
        #     response['Access-Control-Allow-Credentials'] = "true"
        #     response['Access-Control-Allow-Headers'] = 'Content-Type,X-Requested-With,X-CSRFToken,code,date,token'
        #     response['Access-Control-Allow-Methods'] = 'POST,PUT,PATCH,DELETE,GET,OPTIONS'
        return response
