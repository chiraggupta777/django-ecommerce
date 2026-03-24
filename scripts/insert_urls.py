from pathlib import Path

path = Path(__file__).resolve().parent.parent / "msdhoni" / "urls.py"
text = path.read_text(encoding="utf-8")
marker = "    path('cart/update/', views.update_cart, name='update_cart'),\n]"
insert = "    path('cart/clear/', views.clear_cart, name='clear_cart'),\n    path('checkout/', views.checkout, name='checkout'),\n    path('checkout/complete/', views.checkout_complete, name='checkout_complete'),\n]"

if marker not in text:
    raise SystemExit(f'Marker not found in {path}\nExpected marker:\n{marker!r}')

path.write_text(text.replace(marker, insert), encoding='utf-8')
print('Inserted checkout/clear routes into urls.py')
