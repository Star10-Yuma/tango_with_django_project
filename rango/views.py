from django.shortcuts import render

from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from django.shortcuts import redirect
from django.urls import reverse

def index(request):
    #Construct a dictionary to pass to the template engine as its context.
    #The key boldmessage matches to the  {{boldmessage}} in the template

    #This queries the database for all categories stored then orders them by their likes in descending order
    #Then outputs the top 5 only
    #Placing this variable in our context deictionary will alow it to be passed by the template engine
    category_list= Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = pages_list


    #Returns a rendered response to send to the client
    #We make use of the shortcut function to simplify the code
    #The first parameter is the template we wish to use
    return render(request, 'rango/index.html', context = context_dict)

def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Hussain ALFAYLY'}
    return render(request, 'rango/about.html',context = context_dict)

def show_category(request, category_name_slug):
    #creating a context dictionary to pass to the template rendering engine
    context_dict = {}

    try:
        #we try finding a category name slug with the given name
        #if not it throws a DoesNotExist exception
        #The .get() method is to return one model isntance else an exception is raised
        category = Category.objects.get(slug=category_name_slug)

        #This will get all the pages connected to that category or else it just returns an empty list
        pages = Page.objects.filter(category=category)

        #Adds the list to the context dictionary under the name pages
        context_dict['pages'] = pages

        #We add the category object to our context dictionary to verify that it exists
        context_dict['category'] = category

    except Category.DoesNotExist:
        #In here if the category does not exist then the context dictionary will display nothing for the pages and categories
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context = context_dict )


def add_category(request):
    form = CategoryForm()

    #HTTP POST
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #Validates if we have been provided with a valid form
        if form.is_valid():
            #Save the new Category to the database
            cat = form.save(commit=True)
            print(cat, cat.slug)
            #This redirects the user back to the index view
            return redirect('/rango/')
        else:
            #The supplied form contained errors so just print them to the terminal
            print(form.errors)

        #Returns the bad form, new form or no form supplied cases
        #Render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)

    except Category.DoesNotExist:
        category = None

    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category',kwargs={'category_name_slug':category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
