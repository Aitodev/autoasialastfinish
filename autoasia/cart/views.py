from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Bestproduct, Product
from django.views import View
from .cart import Cart
import telebot
from .forms import CartAddProductForm, OrderSendForm

#1387522266:AAHTqKbJzHhhwqwsi7-q8oCD-cxKMwj4k04
bot = telebot.TeleBot("1387522266:AAHTqKbJzHhhwqwsi7-q8oCD-cxKMwj4k04")


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product,  id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'],
                     'update': True})
    context = {
        'cart': cart
    }
    return render(request, 'cart/cart.html', context)


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')


def order(request):
    cart = Cart(request)
    context = {
        'cart': cart
    }
    return render(request, 'cart/checkout.html', context)


class OrderSendView(View):
    def post(self, request):
        if request.method == 'POST':
            form = OrderSendForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data['phone']
                cart = Cart(request)
                message = 'Поступил новый заказ!\r\n\r\nТелефон: ' + phone + '\r\n'  + '\r\n\r\nПродукты\r\n\r\n'

                for c in cart:
                    message += 'Название: ' + str(c['product']) + '\r\n'
                    message += 'Цена: ' + str(c['price']) + '\r\n\r\n'
                    message += 'Количество: ' + str(c['quantity']) + '\r\n\r\n'

                message += 'Общая стоимость: ' + str(cart.get_total_price())

                bot.send_message(-387514692, message)
                Cart.clear(cart)
                return redirect('main:index')
            return redirect('main:index')
