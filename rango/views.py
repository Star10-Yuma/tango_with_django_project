from django.shortcuts import render

from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

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

    visitor_cookie_handler(request)

    #Returns a rendered response to send to the client
    #We make use of the shortcut function to simplify the code
    #The first parameter is the template we wish to use
    # get our response object so that we can add the cookie information
    return render(request, 'rango/index.html', context = context_dict)

def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Hussain ALFAYLY'}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
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

@login_required
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

@login_required
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

def register(request):
    #Boolean value to indicate if the registration was successful or not
    #Set to false initially then changes to true when it is successful
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            #Saves the users form data to the database if valid
            user = user_form.save()

            #Now we hash the user password and then update the user object
            user.set_password(user.password)
            user.save()

            #Now we sort out and check if the UserProfile instance uploaded a picture or not
            #We set the commit to false until after the picture check is done

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            #Now we save the UserProfile instance
            profile.save()

            #Updated registered to show that the form has been successful
            registered = True

        else:
            #prints any mistakes/invalid forms in the terminal
            print(user_form.errors, profile_form.errors)

    else:
        #Not a HTTP Post so we render the form using the two ModelForm instances so they are ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})\

def user_login(request):
    if request.method == 'POST':
        #Takes the username and password inputted to authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Using django engine it checks if this combination is valid and returns the User object if it is
        user = authenticate(username=username, password=password)

        #Now if the user object is in our database it will check if it is active or not
        if user:
            if user.is_active:
                #user may login if active
                login(request,user)
                return redirect(reverse('rango:index'))

            else:
                #else account inactive so no logging in
                return HttpResponse("Your Rango account is disabled")

        else:
            #invalid login details provided so no logging in
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    #if the scenario was a HTTP GET
    else:
        #No context variables to return hence blank dictionary object so no third parameter
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    #Since we know the user is logged in we can now just log them out
    logout(request)
    #Takes the user back to the homepage
    return redirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val
def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(get_server_side_cookie(request, 'visits','1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    #if its been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        #Update the last visit cookie as we updated the visit counter
        request.session['last_visit'] = str(datetime.now())

    else:
        request.session['last_visit'] = last_visit_cookie

    #Updates/sets the visits cookie
    request.session['visits'] = visits
