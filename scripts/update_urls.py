from pathlib import Path

path = Path(__file__).resolve().parent.parent / "msdhoni" / "urls.py"
text = path.read_text(encoding="utf-8")
old = "    path('cart/remove/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),\r\n    path('cart/update/', views.update_cart, name='update_cart'),\r\n]"
new = "    path('cart/remove/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),\r\n    path('cart/update/', views.update_cart, name='update_cart'),\r\n    path('cart/clear/', views.clear_cart, name='clear_cart'),\r\n    path('checkout/', views.checkout, name='checkout'),\r\n    path('checkout/complete/', views.checkout_complete, name='checkout_complete'),\r\n]"

if old not in text:
    raise SystemExit('Expected segment not found')

path.write_text(text.replace(old, new), encoding='utf-8')
print('urls.py updated')
