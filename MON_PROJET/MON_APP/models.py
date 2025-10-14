from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} x{self.quantity}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('en attente', 'En attente'),
        ('confirmée', 'Confirmée'),
        ('en préparation', 'En préparation'),
        ('en livraison', 'En livraison'),
        ('livrée', 'Livrée'),
        ('annulée', 'Annulée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='en attente')
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Date de livraison")
    order_number = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Numéro de commande")
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Méthode de paiement")

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Générer un numéro unique basé sur l'ID (sera défini après sauvegarde initiale)
            super().save(*args, **kwargs)
            self.order_number = f"CMD{self.id:06d}"
            # Éviter la récursion en utilisant update
            Order.objects.filter(pk=self.pk).update(order_number=self.order_number)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.order_number} - {self.user.username}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.book.title} x{self.quantity} (Order #{self.order.id})"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'book'),)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}: {self.stars}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.book.title}: {self.text[:30]}"
