from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

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
      if not image:
         return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
      try:
         result = predict(image)
         return JsonResponse({'success': True, 'result': result})
      except Exception as e:
         return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
   
   return render(request, "zucchini/index.html" , context)