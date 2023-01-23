from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    #Construct a dictionary to pass to the template engine as its context.
    #The key boldmessage matches to the  {{boldmessage}} in the template
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}

    #Returns a rendered response to send to the client
    #We make use of the shortcut function to simplify the code
    #The first parameter is the template we wish to use
    return render(request, 'rango/index.html', context = context_dict)

def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Hussain ALFAYLY'}
    return render(request, 'rango/about.html',context_dict)