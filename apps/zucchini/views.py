from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .source.predictor import predict
from .source.model import load_model


def index(request):
   result = None

   context = {
          'model_load_status':'Success'
   }
   
       
   
   if request.method == "POST":
      image = request.FILES.get("image")
       
      result = predict(image)
      context['result'] = result
      return render(request, "zucchini/index.html", context)
    
   
   return render(request, "zucchini/index.html" , context)