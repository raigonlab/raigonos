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


class ArtworkGalleryViewTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user('gallery_owner', password='pass12345')
        published = Collection.objects.create(
            owner=owner, title='Published Collection', status=Collection.STATUS_PUBLISHED
        )
        draft = Collection.objects.create(
            owner=owner, title='Draft Collection', status=Collection.STATUS_DRAFT
        )
        Artwork.objects.create(
            collection=published, title='Visible Piece', image=tiny_image()
        )
        Artwork.objects.create(
            collection=draft, title='Hidden Piece', image=tiny_image()
        )

    def test_is_the_site_root(self):
        response = self.client.get('/')
        self.assertEqual(response.resolver_match.view_name, 'gallery:artwork_gallery')

    def test_only_shows_artworks_from_published_collections(self):
        response = self.client.get(reverse('gallery:artwork_gallery'))
        self.assertContains(response, 'Visible Piece')
        self.assertNotContains(response, 'Hidden Piece')


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


class DashboardSearchTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('searcher', password='pass12345')
        self.client.login(username='searcher', password='pass12345')
        Collection.objects.create(owner=self.owner, title='Nightfall Studies')
        Collection.objects.create(owner=self.owner, title='Untitled Sketches')

    def test_no_query_shows_everything(self):
        response = self.client.get(reverse('gallery:dashboard'))
        self.assertContains(response, 'Nightfall Studies')
        self.assertContains(response, 'Untitled Sketches')

    def test_query_filters_by_title_case_insensitive(self):
        response = self.client.get(reverse('gallery:dashboard'), {'q': 'night'})
        self.assertContains(response, 'Nightfall Studies')
        self.assertNotContains(response, 'Untitled Sketches')


class CollectionManageViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('manager', password='pass12345')
        self.other_user = User.objects.create_user('rival', password='pass12345')
        self.collection = Collection.objects.create(
            owner=self.owner, title='My Collection'
        )
        self.artwork = Artwork.objects.create(
            collection=self.collection, title='Piece I', image=tiny_image()
        )

    def test_requires_login(self):
        url = reverse('gallery:collection_manage', args=[self.collection.slug])
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_other_user_gets_404(self):
        self.client.login(username='rival', password='pass12345')
        url = reverse('gallery:collection_manage', args=[self.collection.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_owner_sees_its_artworks(self):
        self.client.login(username='manager', password='pass12345')
        url = reverse('gallery:collection_manage', args=[self.collection.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Piece I')


class ArtworkManageViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('curator', password='pass12345')
        self.other_user = User.objects.create_user('outsider', password='pass12345')
        self.collection = Collection.objects.create(
            owner=self.owner, title='Sequence'
        )
        self.first = Artwork.objects.create(
            collection=self.collection,
            title='First',
            image=tiny_image(),
            display_order=1,
        )
        self.second = Artwork.objects.create(
            collection=self.collection,
            title='Second',
            image=tiny_image(),
            display_order=2,
        )
        self.third = Artwork.objects.create(
            collection=self.collection,
            title='Third',
            image=tiny_image(),
            display_order=3,
        )

    def test_requires_login(self):
        url = reverse('gallery:artwork_manage', args=[self.second.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_other_user_gets_404(self):
        self.client.login(username='outsider', password='pass12345')
        url = reverse('gallery:artwork_manage', args=[self.second.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_middle_artwork_has_both_neighbours(self):
        self.client.login(username='curator', password='pass12345')
        url = reverse('gallery:artwork_manage', args=[self.second.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['previous_artwork'], self.first)
        self.assertEqual(response.context['next_artwork'], self.third)

    def test_first_artwork_has_no_previous(self):
        self.client.login(username='curator', password='pass12345')
        url = reverse('gallery:artwork_manage', args=[self.first.pk])
        response = self.client.get(url)
        self.assertIsNone(response.context['previous_artwork'])
        self.assertEqual(response.context['next_artwork'], self.second)


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


class EditFormThumbnailTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('thumb_owner', password='pass12345')
        self.client.login(username='thumb_owner', password='pass12345')
        self.collection = Collection.objects.create(owner=self.owner, title='Thumbs')
        self.artwork = Artwork.objects.create(
            collection=self.collection, title='Pic', image=tiny_image()
        )

    def test_artwork_edit_form_shows_current_image_thumbnail(self):
        response = self.client.get(
            reverse('gallery:artwork_update', args=[self.artwork.pk])
        )
        self.assertContains(response, 'dash-image-preview')
        self.assertContains(response, self.artwork.image.url)
        self.assertNotContains(response, 'Currently:')

    def test_new_artwork_form_has_no_thumbnail(self):
        response = self.client.get(
            reverse('gallery:artwork_create', args=[self.collection.slug])
        )
        self.assertNotContains(response, 'dash-image-preview')


class ArtworkListViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('lister', password='pass12345')
        self.other_user = User.objects.create_user('someone_else', password='pass12345')
        self.collection = Collection.objects.create(owner=self.owner, title='Mine')
        self.own_artwork = Artwork.objects.create(
            collection=self.collection, title='My Piece', image=tiny_image()
        )
        other_collection = Collection.objects.create(
            owner=self.other_user, title='Not Mine'
        )
        self.other_artwork = Artwork.objects.create(
            collection=other_collection, title='Their Piece', image=tiny_image()
        )

    def test_requires_login(self):
        response = self.client.get(reverse('gallery:artwork_list'))
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('gallery:artwork_list')}"
        )

    def test_only_shows_own_artworks(self):
        self.client.login(username='lister', password='pass12345')
        response = self.client.get(reverse('gallery:artwork_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Piece')
        self.assertNotContains(response, 'Their Piece')

    def test_query_filters_by_title_case_insensitive(self):
        self.client.login(username='lister', password='pass12345')
        Artwork.objects.create(
            collection=self.collection, title='Second Piece', image=tiny_image()
        )
        response = self.client.get(reverse('gallery:artwork_list'), {'q': 'my'})
        self.assertContains(response, 'My Piece')
        self.assertNotContains(response, 'Second Piece')


class CollectionArchiveTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('keeper', password='pass12345')
        self.other_user = User.objects.create_user('nosy', password='pass12345')
        self.archived = Collection.objects.create(
            owner=self.owner,
            title='Stored Away',
            status=Collection.STATUS_ARCHIVED,
        )
        Artwork.objects.create(
            collection=self.archived, title='Kept Piece', image=tiny_image()
        )
        self.active = Collection.objects.create(
            owner=self.owner,
            title='Active Work',
            status=Collection.STATUS_PUBLISHED,
        )

    def test_archived_collection_is_hidden_from_public_pages(self):
        home = self.client.get(reverse('gallery:artwork_gallery'))
        listing = self.client.get(reverse('gallery:collection_list'))
        detail = self.client.get(
            reverse('gallery:collection_detail', args=[self.archived.slug])
        )
        self.assertNotContains(home, 'Kept Piece')
        self.assertNotContains(listing, 'Stored Away')
        self.assertEqual(detail.status_code, 404)

    def test_dashboard_excludes_archived_collections(self):
        self.client.login(username='keeper', password='pass12345')
        response = self.client.get(reverse('gallery:dashboard'))
        self.assertContains(response, 'Active Work')
        self.assertNotContains(response, 'Stored Away')

    def test_archive_list_requires_login(self):
        url = reverse('gallery:collection_archive_list')
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_archive_list_shows_only_archived_collections(self):
        self.client.login(username='keeper', password='pass12345')
        response = self.client.get(reverse('gallery:collection_archive_list'))
        self.assertContains(response, 'Stored Away')
        self.assertNotContains(response, 'Active Work')

    def test_archive_action_sets_status_via_post_only(self):
        self.client.login(username='keeper', password='pass12345')
        url = reverse('gallery:collection_archive', args=[self.active.slug])
        self.client.get(url)
        self.active.refresh_from_db()
        self.assertEqual(self.active.status, Collection.STATUS_PUBLISHED)
        self.client.post(url)
        self.active.refresh_from_db()
        self.assertEqual(self.active.status, Collection.STATUS_ARCHIVED)

    def test_other_user_cannot_archive_someone_elses_collection(self):
        self.client.login(username='nosy', password='pass12345')
        url = reverse('gallery:collection_archive', args=[self.active.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.active.refresh_from_db()
        self.assertEqual(self.active.status, Collection.STATUS_PUBLISHED)

    def test_unarchive_restores_to_draft_not_published(self):
        self.client.login(username='keeper', password='pass12345')
        url = reverse('gallery:collection_unarchive', args=[self.archived.slug])
        self.client.post(url)
        self.archived.refresh_from_db()
        self.assertEqual(self.archived.status, Collection.STATUS_DRAFT)
