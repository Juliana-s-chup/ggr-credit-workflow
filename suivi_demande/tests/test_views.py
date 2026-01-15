"""
Tests des vues de l'application suivi_demande.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import (
    DossierCredit,
    DossierStatutAgent,
    UserProfile,
    UserRoles,
    Notification,
)

User = get_user_model()


class ViewsAccessTestCase(TestCase):
    """Tests d'accès aux vues."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.client = Client()
        
        # Créer un client
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123'
        )
        self.client_profile = UserProfile.objects.create(
            user=self.client_user,
            full_name="Client Test",
            phone="+242 06 111 11 11",
            address="Test Address",
            role=UserRoles.CLIENT
        )
        
        # Créer un gestionnaire
        self.gest_user = User.objects.create_user(
            username='gestionnaire',
            email='gest@test.com',
            password='testpass123'
        )
        self.gest_profile = UserProfile.objects.create(
            user=self.gest_user,
            full_name="Gestionnaire Test",
            phone="+242 06 222 22 22",
            address="Test",
            role=UserRoles.GESTIONNAIRE
        )
    
    def test_home_accessible_sans_connexion(self):
        """Test que la page d'accueil redirige vers login."""
        response = self.client.get('/')
        # La racine redirige vers login
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_require_login(self):
        """Test que le dashboard nécessite une connexion."""
        response = self.client.get('/dashboard/')
        # Doit rediriger vers login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_dashboard_accessible_when_logged_in(self):
        """Test que le dashboard est accessible une fois connecté."""
        self.client.login(username='client', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_my_applications_require_login(self):
        """Test que my_applications nécessite une connexion."""
        response = self.client.get('/mes-dossiers/')
        self.assertEqual(response.status_code, 302)
    
    def test_my_applications_accessible_when_logged_in(self):
        """Test que my_applications est accessible connecté."""
        self.client.login(username='client', password='testpass123')
        response = self.client.get('/mes-dossiers/')
        self.assertEqual(response.status_code, 200)


class DashboardViewTestCase(TestCase):
    """Tests du dashboard."""
    
    def setUp(self):
        """Préparation."""
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='pass')
        self.profile = UserProfile.objects.create(
            user=self.user,
            full_name="Test User",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT
        )
    
    def test_dashboard_client_affiche_ses_dossiers(self):
        """Test que le dashboard client affiche ses dossiers."""
        # Créer 3 dossiers pour ce client
        for i in range(3):
            DossierCredit.objects.create(
                client=self.user,
                reference=f"DOS-TEST-{i:03d}",
                produit="Crédit",
                montant=Decimal('1000000.00')
            )
        
        self.client.login(username='testuser', password='pass')
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        # Vérifier que les dossiers sont dans le contexte
        self.assertIn('dossiers_en_cours', response.context)
        self.assertEqual(response.context['dossiers_en_cours'].count(), 3)
    
    def test_dashboard_client_ne_voit_pas_dossiers_autres(self):
        """Test qu'un client ne voit pas les dossiers des autres."""
        # Créer un autre client
        other_user = User.objects.create_user('other', password='pass')
        UserProfile.objects.create(
            user=other_user,
            full_name="Other",
            phone="+242 06 000 00 01",
            address="Test",
            role=UserRoles.CLIENT
        )
        
        # Créer un dossier pour l'autre client
        DossierCredit.objects.create(
            client=other_user,
            reference="DOS-OTHER-001",
            produit="Crédit",
            montant=Decimal('500000.00')
        )
        
        # Se connecter avec le premier client
        self.client.login(username='testuser', password='pass')
        response = self.client.get('/dashboard/')
        
        # Vérifier qu'il ne voit pas le dossier de l'autre
        self.assertEqual(response.context['dossiers_en_cours'].count(), 0)


class PaginationTestCase(TestCase):
    """Tests de la pagination."""
    
    def setUp(self):
        """Préparation."""
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='pass')
        UserProfile.objects.create(
            user=self.user,
            full_name="Test",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT
        )
    
    def test_my_applications_pagination_page_1(self):
        """Test que la pagination fonctionne sur page 1."""
        # Créer 30 dossiers
        for i in range(30):
            DossierCredit.objects.create(
                client=self.user,
                reference=f"DOS-{i:03d}",
                produit="Crédit",
                montant=Decimal('1000000.00')
            )
        
        self.client.login(username='testuser', password='pass')
        response = self.client.get('/mes-dossiers/?page=1')
        
        self.assertEqual(response.status_code, 200)
        # Vérifier qu'il y a 25 dossiers (ITEMS_PER_PAGE)
        dossiers = response.context['dossiers']
        self.assertEqual(len(dossiers), 25)
        # Vérifier qu'il y a une page suivante
        self.assertTrue(dossiers.has_next())
    
    def test_my_applications_pagination_page_2(self):
        """Test que la page 2 fonctionne."""
        # Créer 30 dossiers
        for i in range(30):
            DossierCredit.objects.create(
                client=self.user,
                reference=f"DOS-{i:03d}",
                produit="Crédit",
                montant=Decimal('1000000.00')
            )
        
        self.client.login(username='testuser', password='pass')
        response = self.client.get('/mes-dossiers/?page=2')
        
        self.assertEqual(response.status_code, 200)
        # Vérifier qu'il y a 5 dossiers restants
        dossiers = response.context['dossiers']
        self.assertEqual(len(dossiers), 5)
        # Vérifier qu'il n'y a pas de page suivante
        self.assertFalse(dossiers.has_next())


class NotificationsViewTestCase(TestCase):
    """Tests des vues de notifications."""
    
    def setUp(self):
        """Préparation."""
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='pass')
        UserProfile.objects.create(
            user=self.user,
            full_name="Test",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT
        )
    
    def test_notifications_list_accessible(self):
        """Test que la liste des notifications est accessible."""
        self.client.login(username='testuser', password='pass')
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
    
    def test_notifications_list_affiche_notifications_utilisateur(self):
        """Test que seules les notifications de l'utilisateur sont affichées."""
        # Créer 3 notifications pour cet utilisateur
        for i in range(3):
            Notification.objects.create(
                utilisateur_cible=self.user,
                type="TEST",
                titre=f"Test {i}",
                message="Message test",
                canal="INTERNE"
            )
        
        # Créer une notification pour un autre utilisateur
        other_user = User.objects.create_user('other', password='pass')
        Notification.objects.create(
            utilisateur_cible=other_user,
            type="TEST",
            titre="Other",
            message="Message",
            canal="INTERNE"
        )
        
        self.client.login(username='testuser', password='pass')
        response = self.client.get('/notifications/')
        
        # Vérifier qu'il y a 3 notifications
        notifications = response.context['notifications']
        self.assertEqual(notifications.count(), 3)
    
    def test_mark_all_read_fonctionne(self):
        """Test que marquer toutes les notifications comme lues fonctionne."""
        # Créer 3 notifications non lues
        for i in range(3):
            Notification.objects.create(
                utilisateur_cible=self.user,
                type="TEST",
                titre=f"Test {i}",
                message="Message",
                canal="INTERNE",
                lu=False
            )
        
        self.client.login(username='testuser', password='pass')
        response = self.client.post('/notifications/mark-all/')
        
        # Vérifier la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que toutes sont lues
        unread_count = Notification.objects.filter(
            utilisateur_cible=self.user,
            lu=False
        ).count()
        self.assertEqual(unread_count, 0)


class DossierDetailViewTestCase(TestCase):
    """Tests de la vue détail dossier."""
    
    def setUp(self):
        """Préparation."""
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='pass')
        UserProfile.objects.create(
            user=self.user,
            full_name="Test",
            phone="+242 06 000 00 00",
            address="Test",
            role=UserRoles.CLIENT
        )
        
        self.dossier = DossierCredit.objects.create(
            client=self.user,
            reference="DOS-DETAIL-001",
            produit="Crédit",
            montant=Decimal('1000000.00')
        )
    
    def test_dossier_detail_accessible_par_proprietaire(self):
        """Test que le propriétaire peut voir son dossier."""
        self.client.login(username='testuser', password='pass')
        response = self.client.get(f'/dashboard/dossier/{self.dossier.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dossier.reference)
    
    def test_dossier_detail_refuse_autre_client(self):
        """Test qu'un autre client ne peut pas voir le dossier."""
        # Créer un autre client
        other_user = User.objects.create_user('other', password='pass')
        UserProfile.objects.create(
            user=other_user,
            full_name="Other",
            phone="+242 06 000 00 01",
            address="Test",
            role=UserRoles.CLIENT
        )
        
        # Se connecter avec l'autre client
        self.client.login(username='other', password='pass')
        response = self.client.get(f'/dashboard/dossier/{self.dossier.pk}/')
        
        # Doit être refusé
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_dossier_detail_accessible_par_gestionnaire(self):
        """Test qu'un gestionnaire peut voir tous les dossiers."""
        # Créer un gestionnaire
        gest_user = User.objects.create_user('gest', password='pass')
        UserProfile.objects.create(
            user=gest_user,
            full_name="Gestionnaire",
            phone="+242 06 222 22 22",
            address="Test",
            role=UserRoles.GESTIONNAIRE
        )
        
        self.client.login(username='gest', password='pass')
        response = self.client.get(f'/dashboard/dossier/{self.dossier.pk}/')
        self.assertEqual(response.status_code, 200)


class SignupViewTestCase(TestCase):
    """Tests de la vue d'inscription."""
    
    def test_signup_page_accessible(self):
        """Test que la page d'inscription est accessible."""
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)
    
    def test_signup_cree_utilisateur(self):
        """Test que l'inscription crée un utilisateur."""
        response = self.client.post('/accounts/signup/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        
        # Vérifier que l'utilisateur existe
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )
