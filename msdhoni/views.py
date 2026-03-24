from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .models import Phone, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


CATEGORY_LABELS = {
    Phone.CATEGORY_MOBILE: "Mobiles",
    Phone.CATEGORY_ACCESSORY: "Accessories",
    Phone.CATEGORY_EARBUDS: "Earbuds",
    Phone.CATEGORY_CHARGER: "Chargers",
}


def _cart_session_key(request):
    """Return a unique cart key so each logged-in user has their own cart."""
    if request.user.is_authenticated:
        return f"cart_user_{request.user.id}"
    return "cart_guest"


def _get_cart(request):
    return request.session.get(_cart_session_key(request), {})


def _save_cart(request, cart):
    key = _cart_session_key(request)
    request.session[key] = cart
    # Keep this for backward compatibility with existing template/cart count usage.
    request.session["cart"] = cart


def _build_cart_items(cart):
    items = []
    total = 0
    phones = Phone.objects.filter(slug__in=cart.keys())
    for phone in phones:
        quantity = cart.get(phone.slug, 0)
        subtotal = phone.price * quantity
        items.append({"phone": phone, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return items, total

def home(request):
    """Home page showing featured products and quick categories."""
    featured = Phone.objects.filter(category=Phone.CATEGORY_MOBILE)[:8]
    return render(request, "msdhoni/home.html", {"phones": featured})

def mobiles(request):
    """List all mobiles."""
    return category_products(request, Phone.CATEGORY_MOBILE)

def accessories(request):
    """List all accessories."""
    return category_products(request, Phone.CATEGORY_ACCESSORY)


def category_products(request, category):
    """Dynamic category listing page."""
    category = category.strip().lower()
    if category not in CATEGORY_LABELS:
        return redirect("home")

    products = Phone.objects.filter(category=category)
    context = {
        "products": products,
        "category_key": category,
        "category_name": CATEGORY_LABELS[category],
    }
    return render(request, "msdhoni/category.html", context)


def deals(request):
    """Display products with special discounts and deals."""
    sort_by = request.GET.get("sort", "").strip()

    # Fetch products with optional sorting
    all_products = Phone.objects.all()
    if sort_by == "discount":
        all_products = all_products.order_by("-discount_percent")
    elif sort_by == "ending":
        all_products = all_products.order_by("deal_end_time")
    
    # Add discount information to each product
    deals_list = []
    
    for product in all_products:
        # Use the discount_percent from the product model
        discount_percent = product.discount_percent
        
        # If no discount is set, skip or use default
        if discount_percent > 0:
            discount_amount = int(product.price * discount_percent / 100)
            discounted_price = product.price - discount_amount
            
            deals_list.append({
                'product': product,
                'original_price': product.price,
                'discounted_price': discounted_price,
                'discount_percent': discount_percent,
                'savings': discount_amount,
            })
    
    return render(
        request,
        "msdhoni/deals.html",
        {
            "deals": deals_list,
            "current_sort": sort_by,
        },
    )


def contact(request):
    return render(request, "msdhoni/contact.html")


def product_detail(request, slug):
    phone = get_object_or_404(Phone, slug=slug)
    original_price = phone.price
    discounted_price = phone.discounted_price()
    savings = original_price - discounted_price
    has_discount = phone.is_deal and phone.discount_percent > 0 and savings > 0

    # Simple deterministic stock indicator for UI urgency.
    stock_left = (phone.id % 6) + 3 if phone.id else 5

    context = {
        "phone": phone,
        "original_price": original_price,
        "discounted_price": discounted_price,
        "savings": savings,
        "has_discount": has_discount,
        "stock_left": stock_left,
    }
    return render(request, "msdhoni/product_detail.html", context)


def search(request):
    query = request.GET.get("q", "").strip()
    results = Phone.objects.none()
    if query:
        results = Phone.objects.filter(name__icontains=query)
    return render(request, "msdhoni/search.html", {"query": query, "results": results})


def cart(request):
    cart = _get_cart(request)
    items, total = _build_cart_items(cart)
    return render(request, "msdhoni/cart.html", {"items": items, "total": total})


def add_to_cart(request, slug):
    cart = _get_cart(request)
    cart[slug] = cart.get(slug, 0) + 1
    _save_cart(request, cart)
    return redirect("cart")


def remove_from_cart(request, slug):
    cart = _get_cart(request)
    if slug in cart:
        del cart[slug]
        _save_cart(request, cart)
    return redirect("cart")


def update_cart(request):
    if request.method == "POST":
        slug = request.POST.get("slug")
        try:
            quantity = int(request.POST.get("quantity", 0))
        except (TypeError, ValueError):
            quantity = 0

        cart = _get_cart(request)
        if not slug:
            return redirect("cart")

        if quantity <= 0:
            cart.pop(slug, None)
        else:
            cart[slug] = quantity

        _save_cart(request, cart)

    return redirect("cart")


def clear_cart(request):
    _save_cart(request, {})
    return redirect("cart")


@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        return redirect("cart")

    items, total = _build_cart_items(cart)
    return render(request, "msdhoni/checkout.html", {"items": items, "total": total})


@login_required
def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    cart = _get_cart(request)
    if not cart:
        return redirect("cart")

    address = request.POST.get("address", "").strip()
    if not address:
        items, total = _build_cart_items(cart)
        return render(
            request,
            "msdhoni/checkout.html",
            {"items": items, "total": total, "error": "Address is required."},
        )

    items, total = _build_cart_items(cart)
    order = Order.objects.create(
        user=request.user,
        total_price=total,
        address=address,
        status=Order.STATUS_PENDING,
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item["phone"],
            quantity=item["quantity"],
            price=item["phone"].price,
        )

    _save_cart(request, {})
    return redirect("checkout_complete", order_id=order.id)


@login_required
def checkout_complete(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )
    return render(request, "msdhoni/checkout_complete.html", {"order": order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "msdhoni/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )
    order_items = []
    for item in order.items.all():
        order_items.append(
            {
                "product": item.product,
                "quantity": item.quantity,
                "price": item.price,
                "line_total": item.quantity * item.price,
            }
        )
    return render(request, "msdhoni/order_detail.html", {"order": order, "order_items": order_items})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    context = {}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not username:
            context["error"] = "Username is required."
        elif not password:
            context["error"] = "Password is required."
        elif User.objects.filter(username=username).exists():
            context["error"] = "Username already exists."
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            login(request, user)
            return redirect("home")

        context["username"] = username
        context["email"] = email

    return render(request, "signup.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    context = {}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        context["error"] = "Invalid username or password."
        context["username"] = username

    return render(request, "login.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")


def cart_count(request):
    count = sum(_get_cart(request).values())
    return JsonResponse({"count": count})