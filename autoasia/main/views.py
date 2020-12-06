from .models import Bestproduct, Brand, Automodel, Category, Product
from django.shortcuts import render, redirect
from cart.forms import CartAddProductForm
from django.core.mail import send_mail
from .forms import ApplicationsForm
from django.views import View
from cart.cart import Cart
import telebot

bot = telebot.TeleBot("1387522266:AAHTqKbJzHhhwqwsi7-q8oCD-cxKMwj4k04")


def index(request):
    products = Bestproduct.objects.all()
    cart_product_form = CartAddProductForm()
    brands = Brand.objects.all()
    cart = Cart(request)
    context = {
        'best': products,
        'brands': brands,
        'cart': cart,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'main/index.html', context)


def about(request):
    return render(request, 'main/about.html')


def shop(request):
    return render(request, 'main/product.html')


def contact(request):
    return render(request, 'main/contact.html')


def automodels(request, brand_pk):
    automodels = Automodel.objects.filter(brand_id=brand_pk)
    context = {
        'automodels': automodels,
        'brand_pk': brand_pk,
    }
    return render(request, 'main/automodels.html', context)


def category(request, brand_pk, model_pk):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'brand_pk': brand_pk,
        'model_pk': model_pk,
    }
    return render(request, 'main/categories.html', context)


def products(request, brand_pk, model_pk, category_pk):
    category = Category.objects.filter(id=category_pk)
    if category.exists():
        if not category.first().depends_on_brands:
            products = Product.objects.filter(category_id=category_pk)
        else:
            products = Product.objects.filter(brand_id=brand_pk, automodel_id=model_pk, category_id=category_pk)
    context = {
        'products': products,
        'brand_pk': brand_pk,
        'model_pk': model_pk,
        'category_pk': category_pk,
    }
    return render(request, 'main/products.html', context)


def product_view(request, product_pk):
    brands = Brand.objects.all()
    product = Product.objects.get(id=product_pk)
    cart_product_form = CartAddProductForm()
    cart = Cart(request)
    context = {
        'cart_product_form': cart_product_form,
        'product_pk': product_pk,
        'product': product,
        'brands': brands,
        'cart': cart,
    }
    return render(request, 'main/product.html', context)


class ApplicationsView(View):
    def post(self, request):
        if request.method == 'POST':
            form = ApplicationsForm(request.POST)
            # print(request.POST)
        if form.is_valid():
            form.save()
            mail = form.cleaned_data['mail']
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            subject = 'Новая заявка!'
            from_email = 'assassinaltair@bk.ru'
            to_email = ['aitofullstackdev@gmail.com', 'aitolivelive@gmail.com']
            message = 'Новая заявка на обратный звонок!' + '\r\n' + '\r\n' + 'Почта: ' + mail + '\r\n' + '\r\n' + 'Имя:' + name + '\r\n' + '\r\n' + 'Номер телефона: ' + phone
            # send_mail(subject, message, from_email, to_email, fail_silently=False)
            bot.send_message(-387514692, message)
        return redirect('main:contact')
