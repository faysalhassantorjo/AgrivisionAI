from django.shortcuts import render
from django.http import HttpResponse

from .source.predictor import predict
from .source.model import load_model

# Create your views here.
def index(request):
   result = None

   context = {
          'model_load_status':'Success'
   }
   
       
   
   if request.method == "POST":
      image = request.FILES.get("image")
       
      result = predict(image)
      context['result'] = result
      return render(request, "index.html", context)
    
   
   return render(request, "papaya/index.html" , context)