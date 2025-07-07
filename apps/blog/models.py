from django.db import models
from django.utils import timezone
import uuid
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

#SIEMRPE QUE SE HACE UN CAMBIO HACER python manage.py makemigrations y python manage.py migrate
#direccion donde se gureadara las imagenes del post
def blog_thumbnail_directory(instance, filename):
    return "blog/{0}/{1}".format(instance.title, filename)

#direccion donde se gureadara las imagenes de la category
def category_thumbnail_directory(instance, filename):
    return "blog_categories/{0}/{1}".format(instance.name, filename)

class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)

    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to=category_thumbnail_directory, blank=True, null=True)
    slug = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Post(models.Model):

    class PostObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status='published')

    status_options = (
        ("draft", "Draft"),
        ("published", "Published")
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    content = CKEditor5Field('Content', config_name='default')
    thumbnail = models.ImageField(upload_to=blog_thumbnail_directory)
    keywords = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=status_options, default='draft')

    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    objects = models.Manager() #default  manager
    postObjects = PostObjects() #xustom manager

    class Meta:
        ordering = ("status", "-created_at")

    def __str__(self):
        return self.title
    
class Heading(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='headings')
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    level = models.IntegerField(
        choices=(
            (1, "H1"),
            (2, "H2"),
            (3, "H3"),
            (4, "H4"),
            (5, "H5"),
            (6, "H6"),
        )
    )
    order = models.PositiveBigIntegerField()

    class Meta:
        ordering = ["order"]
    
    #args creo para listas y kwargs para diccionario
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) #slugufy es por ejemplo title= hola a todos; slugify transforma a hola-a-todos 
        super().save(*args, **kwargs)
    
