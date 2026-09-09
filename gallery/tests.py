import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Artwork, Collection

User = get_user_model()


def tiny_image(name='test.png'):
    """Return a minimal valid in-memory PNG for ImageField uploads."""
    buf = io.BytesIO()
    Image.new('RGB', (1, 1)).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class CollectionModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', password='pass12345')

    def test_slug_is_generated_from_title(self):
        collection = Collection.objects.create(
            owner=self.owner, title='Digital Charcoal'
        )
        self.assertEqual(collection.slug, 'digital-charcoal')

    def test_duplicate_titles_get_unique_slugs(self):
        first = Collection.objects.create(owner=self.owner, title='Untitled')
        second = Collection.objects.create(owner=self.owner, title='Untitled')
        self.assertNotEqual(first.slug, second.slug)

    def test_str_returns_title(self):
        collection = Collection.objects.create(owner=self.owner, title='Accord')
        self.assertEqual(str(collection), 'Accord')


class ArtworkModelTests(TestCase):
    def test_str_returns_title(self):
        owner = User.objects.create_user('owner2', password='pass12345')
        collection = Collection.objects.create(owner=owner, title='Vault')
        artwork = Artwork.objects.create(
            collection=collection, title='Untitled I', image=tiny_image()
        )
        self.assertEqual(str(artwork), 'Untitled I')


class PublicGalleryViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('artist', password='pass12345')
        self.published = Collection.objects.create(
            owner=self.owner,
            title='Published Collection',
            status=Collection.STATUS_PUBLISHED,
        )
        self.draft = Collection.objects.create(
            owner=self.owner, title='Draft Collection', status=Collection.STATUS_DRAFT
        )

    def test_collection_list_only_shows_published(self):
        response = self.client.get(reverse('gallery:collection_list'))
        self.assertContains(response, 'Published Collection')
        self.assertNotContains(response, 'Draft Collection')

    def test_draft_collection_detail_is_not_found(self):
        url = reverse('gallery:collection_detail', args=[self.draft.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_published_collection_detail_is_found(self):
        url = reverse('gallery:collection_detail', args=[self.published.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class DashboardPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner3', password='pass12345')
        self.other_user = User.objects.create_user('intruder', password='pass12345')
        self.collection = Collection.objects.create(
            owner=self.owner, title='My Collection'
        )
        self.artwork = Artwork.objects.create(
            collection=self.collection, title='Piece I', image=tiny_image()
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('gallery:dashboard'))
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('gallery:dashboard')}"
        )

    def test_owner_can_view_dashboard(self):
        self.client.login(username='owner3', password='pass12345')
        response = self.client.get(reverse('gallery:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Collection')

    def test_other_user_cannot_edit_collection(self):
        self.client.login(username='intruder', password='pass12345')
        url = reverse('gallery:collection_update', args=[self.collection.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_artwork(self):
        self.client.login(username='intruder', password='pass12345')
        url = reverse('gallery:artwork_delete', args=[self.artwork.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Artwork.objects.filter(pk=self.artwork.pk).exists())


class CollectionCrudTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('creator', password='pass12345')
        self.client.login(username='creator', password='pass12345')

    def test_create_collection(self):
        response = self.client.post(
            reverse('gallery:collection_create'),
            {'title': 'New Collection', 'description': '', 'status': 'draft'},
        )
        self.assertEqual(response.status_code, 302)
        collection = Collection.objects.get(title='New Collection')
        self.assertEqual(collection.owner, self.owner)

    def test_update_collection(self):
        collection = Collection.objects.create(owner=self.owner, title='Old Title')
        url = reverse('gallery:collection_update', args=[collection.slug])
        response = self.client.post(
            url, {'title': 'New Title', 'description': '', 'status': 'draft'}
        )
        self.assertEqual(response.status_code, 302)
        collection.refresh_from_db()
        self.assertEqual(collection.title, 'New Title')

    def test_blank_title_does_not_create_collection(self):
        response = self.client.post(
            reverse('gallery:collection_create'),
            {'title': '', 'description': '', 'status': 'draft'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'title', 'This field is required.')
        self.assertFalse(Collection.objects.filter(owner=self.owner).exists())

    def test_delete_collection_cascades_to_artworks(self):
        collection = Collection.objects.create(owner=self.owner, title='To Delete')
        Artwork.objects.create(
            collection=collection, title='Gone Too', image=tiny_image()
        )
        url = reverse('gallery:collection_delete', args=[collection.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Collection.objects.filter(pk=collection.pk).exists())
        self.assertFalse(Artwork.objects.filter(title='Gone Too').exists())
