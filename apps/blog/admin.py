from django.contrib import admin

# expone los modelos de django para asi crear post
#user admin
#email admin@blog.cl
#pass dany1234

from .models import Category, Post, Heading, PostAnalytics, CategoryAnalytics
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from apps.media.models import Media

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'parent', 'slug', 'thumbnail_preview')
    search_fields = ('name', 'title', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)
    ordering = ('name',)
    readonly_fields = ('id',)
    list_editable = ('title',) #hace  que se pueda editar desde la tabla en admin

@admin.register(CategoryAnalytics)
class CategoryAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'views', 'impressions', 'clicks', 'click_through_rate', 'avg_time_on_page')
    search_fields = ('category__name',)
    readonly_fields = ('category','views','impressions','clicks','click_through_rate','avg_time_on_page')

    def category_name(self, obj):
        return obj.category.name
    
    category_name.short_description = 'Category Name'

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    class Meta:
        model = Post
        fields = '__all__'

#heading en el formulario del post
class HeadingInline(admin.TabularInline):
    model = Heading
    extra = 1
    fields = ('title', 'level', 'order', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)
    
class MediaInLine(admin.TabularInline):
    model = Media
    extra = 1
    fields = ('order', 'name', 'size', 'type', 'key', 'media_type')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'status', 'category', 'created_at', 'updated_at', 'thumbnail_preview')
    search_fields = ('title', 'description', 'content', 'keywords', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'category', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at',)
    fieldsets = (
        ('General Information', {
            'fields': ('title', 'description', 'content', 'keywords', 'slug', 'category')
        }), 
        ('Status & Dates', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )
    inlines = [HeadingInline]#[HeadingInline, MediaInLine]

@admin.register(Heading)
class HeadingAdmin(admin.ModelAdmin):
    list_display = ('title', 'post', 'level', 'order')
    search_fields = ('title', 'post__title')
    list_filter = ('level', 'post')
    ordering = ('post', 'order')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('post_title', 'views', 'impressions', 'clicks', 'click_through_rate', 'avg_time_on_page') #como post_title no pertenece al modelo hay que definirlo en una funcion
    search_fields = ('post__title',)
    readonly_fields = ('views', 'impressions', 'clicks', 'click_through_rate', 'avg_time_on_page')

    def post_title(self, obj): #obj es igual al modelo que se registra admin.register(PostAnalytics)
        return obj.post.title
    
    post_title.short_description = 'Post Title'