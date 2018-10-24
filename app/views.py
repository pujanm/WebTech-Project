from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Product, Profile, Review, Cart
from django.contrib.auth.models import User
from .filters import ProductFilter
from textblob import TextBlob
from collections import OrderedDict
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        p = Profile.objects.all().filter(user=request.user)
        return render(request, 'base.html', {'p': p[0]})
    return render(request, 'base.html', {})

def listProducts(request):
    p = Product.objects.all()
    avg_ratings = []
    products_filtered = ProductFilter(request.GET, queryset=p)
    if request.user.is_authenticated:
        profile = Profile.objects.all().filter(user=request.user)

        context = {
            'products_filtered': products_filtered,
            'p': profile[0]
        }
    else:
        context = {
            'products_filtered': products_filtered,
        }
    return render(request, 'productsList.html', context)

def productDetail(request, id):
    p = Product.objects.all().filter(id=id)
    if request.user.is_authenticated:
        profile = Profile.objects.all().filter(user=request.user)
        reviews = Review.objects.all().filter(product=p[0])
        avg_ratings = []
        for i in p:
            r = Review.objects.all().filter(product=i)
            if len(r) == 0:
                avg_ratings.append(0)
            else:
                count = 0
                total_rating = 0
                for j in r:
                    count += 1
                    total_rating += j.rating
                print(total_rating)
                print(count)
                avg_ratings.append(total_rating / count)

        context = {
            'product': p,
            'p': profile[0],
            'reviews': reviews,
            'avg_ratings': avg_ratings[0]
        }
        if request.POST and not request.POST.get("review"):
            cart = Cart.objects.create(product=p[0], user=request.user)
            cart.save()
            return redirect("cart")
        if request.POST and request.POST.get("review"):
            r = Review.objects.all().filter(product=p[0], user=request.user)
            if len(r) == 0:
                review = request.POST.get("review")
                rating = request.POST.get("rating")
                r = Review.objects.create(
                    product=p[0],
                    user=request.user,
                    rating=rating,
                    review=review
                )
                r.save()
                return render(request, 'productDetail.html', context)
        else:
            return render(request, 'productDetail.html', context)
    return render(request, 'productDetail.html', context)

def signup(request):
    if request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        u = User.objects.all().filter(username=username)
        p = Profile.objects.all().filter(email=email)
        if len(u) != 0 or len(p) != 0:
            return render(request, 'signup.html', {"userExists": "The user already exists."})
        else:
            # print(request.POST)
            user = authenticate(username=username, password=password)
            u = User.objects.create_user(
                username=username,
                password=password,
            )
            u.save()
            userProf = User.objects.all().filter(username=username)
            profile = Profile.objects.create(
                user=userProf[0],
                fname=fname,
                lname=lname,
                email=email,
            )
            profile.save()
            login(request, user)
            return redirect('index')
        return render(request, 'signup.html', {"userExists": ""})
    return render(request, 'signup.html', {"userExists": ""})

def loginUser(request):
    if request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        u = User.objects.all().filter(username=username)
        if len(u) == 0:
            return render(request, 'login.html', {"error": "The user doesn't exists."})
        else:
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                return render(request, 'login.html', {"error": "Wrong Password"})
    return render(request, 'login.html', {'error': ''})

def logoutUser(request):
    logout(request)
    return redirect('index')



def cart(request):
    if request.user.is_authenticated:
        profile = Profile.objects.all().filter(user=request.user)
        cart = Cart.objects.all().filter(user=request.user)
        total = 0

        cart_dict = {}
        for i in cart:
            total += i.product.price
            try:
                if cart_dict[i.product.title]:
                    cart_dict[i.product.title][1] += 1
                    cart_dict[i.product.title][2] += int(i.product.price)
            except KeyError:
                cart_dict[i.product.title] = []
                cart_dict[i.product.title].append(i.product.title)
                cart_dict[i.product.title].append(1)
                cart_dict[i.product.title].append(i.product.price)
        final_cart_list = []
        for i in cart_dict:
            final_cart_list.append(cart_dict[i])
        context = {
            'p': profile[0],
            'cart': cart,
            'cartNew': final_cart_list,
            'totalAmount': total
        }
        return render(request, 'cart.html', context)

def profile(request):
    profile = Profile.objects.all().filter(user=request.user)
    if request.POST:
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        address = request.POST.get("address")
        p = Profile.objects.get(user=request.user)
        p.fname = fname
        p.lname = lname
        p.email = email
        p.address = address
        p.save()
        return render(request, 'profile.html', {'p': profile[0]})
    return render(request, 'profile.html', {'p': profile[0]})


def recommendedProducts(request):
    r = Review.objects.all()
    profile = Profile.objects.all().filter(user=request.user)[0]
    product_sentiment = {}
    for i in r:
        try :
            if product_sentiment[i.product.id]:
                product_sentiment[i.product.id]['total'] += TextBlob(i.review).sentiment.polarity
                product_sentiment[i.product.id]['count'] += 1
        except KeyError:
            product_sentiment[i.product.id] = {}
            product_sentiment[i.product.id]['total'] = TextBlob(i.review).sentiment.polarity
            product_sentiment[i.product.id]['count'] = 1
    for i in product_sentiment:
        product_sentiment[i]['avg'] = product_sentiment[i]['total'] / product_sentiment[i]['count']
    print(product_sentiment)
    product_sorted = sorted(product_sentiment, key=lambda k: product_sentiment[k]['avg'])[::-1]
    print(product_sorted)
    final_list = []
    for i in product_sorted:
        final_list.append(Product.objects.all().filter(id=i)[0])

    return render(request, 'recommendedProducts.html', {'products': final_list, 'p': profile})
