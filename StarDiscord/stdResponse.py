from django.http import HttpResponse
import json

class StdResponse(dict):
    def __init__(self, fileds:dict = {}):
        for key, value in fileds.items():
            self.setItem(key, value)


    def setItem(self, key, value) -> None:
        self[key] = value

    def jumps(self) -> HttpResponse:
        
        return HttpResponse(json.dumps(self), content_type='application/json')


class StdResponseSucceed(StdResponse):
    def __init__(self, fileds:dict = {}):
        super().__init__(fileds)
        self.setItem("status", 1)


class StdResponseFailed(StdResponse):
    def __init__(self, fileds:dict = {}):
        super().__init__(fileds)
        self.setItem("status", 2)