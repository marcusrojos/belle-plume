# Améliorations de la Page Commande - Librairie

## Sélections Utilisateur
- 1. Suivi de commande (statut)
- 3. Planification de livraison (date seulement)
- 4. Historique des commandes
- 5. Modification/Annulation de commande
- 8. Avis clients après livraison
- 10. Amélioration UX

## Tâches à Réaliser

### 1. Mise à jour du Modèle Order
- [x] Ajouter champ `delivery_date` (DateField)
- [x] Ajouter champ `order_number` (CharField unique)
- [x] Ajouter champ `payment_method` (CharField)
- [x] Créer migration

### 2. Mise à jour des Formulaires
- [x] Modifier checkout pour inclure delivery_date
- [x] Validation delivery_date (au moins demain)

### 3. Mise à jour des Vues
- [x] Modifier checkout view pour sauvegarder delivery_date et payment_method
- [ ] Ajouter vue order_history pour utilisateurs connectés
- [ ] Ajouter vue order_detail pour voir détails d'une commande
- [ ] Ajouter vues pour modifier/annuler commande (si status permet)
- [ ] Ajouter vue pour laisser avis après livraison
- [x] Modifier confirmation view pour afficher numéro commande et détails

### 4. Mise à jour des Templates
- [x] confirmation.html : Afficher numéro commande, statut, date livraison, détails commande
- [x] checkout.html : Ajouter champ date livraison
- [ ] Nouveau template order_history.html
- [ ] Nouveau template order_detail.html (pour historique)
- [ ] Nouveau template leave_review.html

### 5. Mise à jour des URLs
- [ ] Ajouter routes pour order_history, order_detail, modify_order, cancel_order, leave_review

### 6. Améliorations UX
- [ ] Optimiser responsive design pour mobile
- [ ] Ajouter animations CSS (transitions, loading states)
- [ ] Améliorer lisibilité (contraste, tailles de police)
- [ ] Ajouter indicateurs visuels pour statuts

### 7. Fonctionnalités Additionnelles
- [ ] Système d'email de confirmation de commande
- [ ] Téléchargement PDF du résumé de commande
- [ ] Notifications SMS (optionnel)

### 8. Tests et Validation
- [ ] Tester le flux complet de commande
- [ ] Vérifier permissions (seulement propriétaire peut modifier)
- [ ] Tester sur mobile
- [ ] Valider emails avec nouvelles infos
