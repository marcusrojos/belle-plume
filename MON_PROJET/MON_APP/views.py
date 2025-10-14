from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Book, CartItem, Order, Favorite
from .models import Rating, Comment
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.core.paginator import Paginator
from django.urls import reverse
from django import forms
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db import models
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render

# Page d'accueil
def index(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)
    return render(request, 'index.html', {'books': books, 'query': query})

# Panier
@login_required
def panier(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render(request, 'panier.html', {'cart_items': cart_items, 'total': total})

# Favoris
@login_required
def favoris(request):
    favoris = Favorite.objects.filter(user=request.user)
    return render(request, 'favoris.html', {'favoris': favoris})

# Profil
@login_required
def profil(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'profil.html', {'orders': orders})

# Checkout
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.book.price * item.quantity for item in cart_items)
    if request.method == 'POST':
        delivery_date = request.POST.get('delivery_date')
        payment_method = request.POST.get('payment_method')

        # Create an order and save items
        order = Order.objects.create(
            user=request.user,
            total=total,
            delivery_date=delivery_date,
            payment_method=payment_method
        )
        for item in cart_items:
            # create OrderItem
            from .models import OrderItem
            OrderItem.objects.create(order=order, book=item.book, quantity=item.quantity, price=item.book.price)
        # clear cart
        cart_items.delete()
        return redirect('confirmation')
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total': total})

# Confirmation de commande
@login_required
def confirmation(request):
    # Get the latest order for the user
    order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, 'confirmation.html', {'order': order})

# Connexion
def login_view(request):
    # Support 'next' parameter so visiting /admin redirects to login and returns after auth
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # Changed from 'email' to 'identifier'
        password = request.POST.get('password')
        user = None

        # Try to authenticate with email first
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

        # If not found by email, try with username
        if user is None:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            # Validate next URL is safe
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('index')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    return render(request, 'login.html', {'next': next_url})


def admin_entry(request):
    """Entry point for /admin — shows login page if anonymous, only superusers allowed."""
    # If not authenticated, redirect to login
    if not request.user.is_authenticated:
        return redirect('login')
    # If authenticated but not superuser, deny access
    if not request.user.is_superuser:
        messages.error(request, "Accès réservé aux superadministrateurs.")
        return redirect('index')
    # Authenticated superuser — show dashboard
    return admin_dashboard(request)
def logout_view(request):
    logout(request)
    return redirect('index')
# Inscription
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('index')
    return render(request, 'register.html')


# AJAX / action endpoints for cart and favorites
def _is_ajax(req):
    # Django 5 removed HttpRequest.is_ajax; use header check
    return req.headers.get('x-requested-with') == 'XMLHttpRequest'


def toggle_favorite(request, book_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    if not request.user.is_authenticated:
        if _is_ajax(request):
            return JsonResponse({'error': 'auth_required'}, status=401)
        return redirect('login')
    book = get_object_or_404(Book, id=book_id)
    fav = Favorite.objects.filter(user=request.user, book=book).first()
    if fav:
        fav.delete()
        return JsonResponse({'status': 'removed', 'book_id': book_id})
    else:
        Favorite.objects.create(user=request.user, book=book)
        return JsonResponse({'status': 'added', 'book_id': book_id})


def add_to_cart(request, book_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    if not request.user.is_authenticated:
        if _is_ajax(request):
            return JsonResponse({'error': 'auth_required'}, status=401)
        return redirect('login')
    book = get_object_or_404(Book, id=book_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    cart_item, created = CartItem.objects.get_or_create(user=request.user, book=book)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    total_items = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'status': 'ok', 'book_id': book_id, 'quantity': cart_item.quantity, 'total_items': total_items})


def rate_book(request, book_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    if not request.user.is_authenticated:
        if _is_ajax(request):
            return JsonResponse({'error': 'auth_required'}, status=401)
        return redirect('login')
    book = get_object_or_404(Book, id=book_id)
    try:
        stars = int(request.POST.get('stars', 0))
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Invalid stars')
    if stars < 1 or stars > 5:
        return HttpResponseBadRequest('Stars must be between 1 and 5')
    rating, created = Rating.objects.update_or_create(user=request.user, book=book, defaults={'stars': stars})
    return JsonResponse({'status': 'ok', 'stars': rating.stars, 'created': created})


def comment_book(request, book_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    if not request.user.is_authenticated:
        if _is_ajax(request):
            return JsonResponse({'error': 'auth_required'}, status=401)
        return redirect('login')
    book = get_object_or_404(Book, id=book_id)
    text = request.POST.get('text', '').strip()
    if not text:
        return HttpResponseBadRequest('Empty comment')
    comment = Comment.objects.create(user=request.user, book=book, text=text)
    return JsonResponse({'status': 'ok', 'comment_id': comment.id, 'text': comment.text, 'created_at': comment.created_at.isoformat()})


def book_meta(request, book_id):
    """Return JSON with average rating and last comments for the book."""
    book = get_object_or_404(Book, id=book_id)
    avg = book.ratings.aggregate(avg=models.Avg('stars'))['avg'] or 0
    comments_qs = book.comments.select_related('user').order_by('-created_at')[:10]
    comments = [{'user': c.user.username, 'text': c.text, 'created_at': c.created_at.isoformat()} for c in comments_qs]
    return JsonResponse({'avg_rating': float(avg), 'comments': comments})


@login_required
def remove_cart_item(request, item_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return JsonResponse({'status': 'deleted', 'item_id': item_id})


@login_required
def update_cart_item(request, item_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    try:
        quantity = int(request.POST.get('quantity', item.quantity))
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Invalid quantity')
    if quantity <= 0:
        item.delete()
        return JsonResponse({'status': 'deleted', 'item_id': item_id})
    item.quantity = quantity
    item.save()
    return JsonResponse({'status': 'updated', 'item_id': item_id, 'quantity': item.quantity})

# Admin dashboard (protégé, à adapter selon ton système d'admin)
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('index')
    # Book creation form
    class BookForm(forms.ModelForm):
        class Meta:
            model = Book
            fields = ['title', 'author', 'price', 'image', 'description']

    form = BookForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_dashboard')

    # Statistics
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
    users = User.objects.all()
    nb_users = users.count()
    commandes_attente = Order.objects.filter(status__icontains='attente').count()
    commandes_livrees = Order.objects.filter(status__icontains='livre').count()
    revenus_totaux = Order.objects.aggregate(total=models.Sum('total'))['total'] or 0
    ventes_jour = Order.objects.filter(created_at__date=timezone.now().date()).aggregate(sum=models.Sum('total'))['sum'] or 0

    # Calculate real payment success rate (orders that are not cancelled)
    total_orders = Order.objects.count()
    successful_orders = Order.objects.exclude(status__icontains='annul').count()
    percent_paiements = int((successful_orders / total_orders * 100) if total_orders else 0)

    # Calculate loyal customers (users with more than 1 order)
    loyal_users = User.objects.annotate(order_count=models.Count('order')).filter(order_count__gt=1).count()
    percent_fideles = int((loyal_users / nb_users * 100) if nb_users else 0)

    # Sessions actives (approximation) — users with non-expired sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []
    for s in sessions:
        data = s.get_decoded()
        uid = data.get('_auth_user_id')
        if uid:
            uid_list.append(uid)
    connected_users = User.objects.filter(id__in=uid_list)
    nb_connected = connected_users.count()

    # prepare last orders for display (with items)
    last_orders = orders[:10]

    context = {
        'form': form,
        'orders': orders,
        'users': users,
        'nb_users': nb_users,
        'commandes_attente': commandes_attente,
        'commandes_livrees': commandes_livrees,
        'revenus_totaux': revenus_totaux,
        'ventes_jour': ventes_jour,
        'nb_connected': nb_connected,
        'connected_users': connected_users,
        'last_orders': last_orders,
        'percent_livrees': int((commandes_livrees / orders.count() * 100) if orders.count() else 0),
        'percent_paiements': percent_paiements,
        'percent_fideles': percent_fideles,
    }
    # Indicate to templates that the base navigation should be hidden on the admin page
    context['hide_base_nav'] = True
    return render(request, 'admin.html', context)


@login_required
def admin_update_order_status(request, order_id):
    if not request.user.is_superuser:
        return redirect('index')
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    order = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    if status:
        order.status = status
        order.save()
    return redirect('admin_dashboard')


# Helper to build shared admin context used by multiple admin views
def _build_admin_context(request):
    # Book creation form (read-only here)
    class BookForm(forms.ModelForm):
        class Meta:
            model = Book
            fields = ['title', 'author', 'price', 'image', 'description']

    form = BookForm()

    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
    users = User.objects.all()
    nb_users = users.count()
    commandes_attente = Order.objects.filter(status__icontains='attente').count()
    commandes_livrees = Order.objects.filter(status__icontains='livre').count()
    revenus_totaux = Order.objects.aggregate(total=models.Sum('total'))['total'] or 0
    ventes_jour = Order.objects.filter(created_at__date=timezone.now().date()).aggregate(sum=models.Sum('total'))['sum'] or 0

    # Sessions actives (approximation)
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []
    for s in sessions:
        data = s.get_decoded()
        uid = data.get('_auth_user_id')
        if uid:
            uid_list.append(uid)
    connected_users = User.objects.filter(id__in=uid_list)
    nb_connected = connected_users.count()

    # Calculate real payment success rate (orders that are not cancelled)
    total_orders = Order.objects.count()
    successful_orders = Order.objects.exclude(status__icontains='annul').count()
    percent_paiements = int((successful_orders / total_orders * 100) if total_orders else 0)

    # Calculate loyal customers (users with more than 1 order)
    loyal_users = User.objects.annotate(order_count=models.Count('order')).filter(order_count__gt=1).count()
    percent_fideles = int((loyal_users / nb_users * 100) if nb_users else 0)

    context = {
        'form': form,
        'orders': orders,
        'users': users,
        'nb_users': nb_users,
        'commandes_attente': commandes_attente,
        'commandes_livrees': commandes_livrees,
        'revenus_totaux': revenus_totaux,
        'ventes_jour': ventes_jour,
        'nb_connected': nb_connected,
        'connected_users': connected_users,
        'last_orders': orders[:10],
        'percent_livrees': int((commandes_livrees / orders.count() * 100) if orders.count() else 0),
        'percent_paiements': percent_paiements,
        'percent_fideles': percent_fideles,
    }
    return context


# Admin subsections
@login_required
def admin_users(request):
    if not request.user.is_superuser:
        return redirect('index')
    context = _build_admin_context(request)
    users_qs = context['users'].order_by('-date_joined')
    paginator = Paginator(users_qs, 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    context.update({'users_page': users_page, 'active_section': 'users', 'hide_base_nav': True})
    return render(request, 'admin.html', context)


@login_required
def admin_orders(request):
    if not request.user.is_superuser:
        return redirect('index')
    context = _build_admin_context(request)
    context['active_section'] = 'orders'
    context['hide_base_nav'] = True
    return render(request, 'admin.html', context)


@login_required
def admin_books(request):
    if not request.user.is_superuser:
        return redirect('index')
    # Book form handling
    class BookForm(forms.ModelForm):
        class Meta:
            model = Book
            fields = ['title', 'author', 'price', 'image', 'description']

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livre ajouté avec succès.')
            return redirect('admin_books')
    else:
        form = BookForm()

    # Get all books for listing
    books = Book.objects.all().order_by('-id')

    context = _build_admin_context(request)
    # override form with the one for books section
    context.update({'form': form, 'books': books, 'active_section': 'books', 'hide_base_nav': True})
    return render(request, 'admin.html', context)


@login_required
def admin_stats(request):
    if not request.user.is_superuser:
        return redirect('index')
    context = _build_admin_context(request)
    context['active_section'] = 'stats'
    context['hide_base_nav'] = True
    return render(request, 'admin.html', context)


@login_required
def admin_sales_data(request):
    """Return JSON data for sales chart."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Get sales data for the last 6 months
    from django.db.models.functions import TruncMonth
    from django.db.models import Sum

    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    sales_data = Order.objects.filter(
        created_at__gte=six_months_ago,
        status__in=['livrée', 'en attente']  # Include successful orders
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_sales=Sum('total')
    ).order_by('month')

    # Prepare labels and data
    labels = []
    data = []
    current = six_months_ago.replace(day=1)
    end = timezone.now().replace(day=1) + timezone.timedelta(days=32)
    end = end.replace(day=1)

    sales_dict = {item['month']: item['total_sales'] for item in sales_data}

    while current < end:
        labels.append(current.strftime('%b %Y'))
        data.append(float(sales_dict.get(current, 0)))
        current += timezone.timedelta(days=32)
        current = current.replace(day=1)

    return JsonResponse({'labels': labels, 'data': data})


@login_required
def admin_user_toggle(request, user_id):
    if not request.user.is_superuser:
        return redirect('index')
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    user = get_object_or_404(User, id=user_id)
    # Prevent changing own staff status
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas modifier votre propre statut.")
        return redirect('admin_users')
    user.is_staff = not user.is_staff
    user.save()
    messages.success(request, f"Statut staff mis à jour pour {user.username}.")
    return redirect('admin_users')


@login_required
def admin_user_delete(request, user_id):
    if not request.user.is_staff:
        return redirect('index')
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('admin_users')
    user.delete()
    messages.success(request, 'Utilisateur supprimé.')
    return redirect('admin_users')


@login_required
def admin_book_edit(request, book_id):
    if not request.user.is_superuser:
        return redirect('index')
    book = get_object_or_404(Book, id=book_id)
    class BookForm(forms.ModelForm):
        class Meta:
            model = Book
            fields = ['title', 'author', 'price', 'image', 'description']

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livre modifié avec succès.')
            return redirect('admin_books')
    else:
        form = BookForm(instance=book)

    context = _build_admin_context(request)
    context.update({'form': form, 'book': book, 'active_section': 'books', 'hide_base_nav': True})
    return render(request, 'admin_book_edit.html', context)


@login_required
def admin_book_delete(request, book_id):
    if not request.user.is_superuser:
        return redirect('index')
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, 'Livre supprimé.')
    return redirect('admin_books')


def custom_404(request, exception):
    """Custom 404 error handler."""
    return render(request, '404.html', status=404)
