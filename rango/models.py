from django.db import models
from django.contrib import admin
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

#Fixes name from categorys to categories in admin page
    class Meta:
        verbose_name_plural = "Categories"

#Outputs the String name of the category object
    def __str__(self):
        return self.name

class Page(models.Model):
    #database fields with their constraints and field types
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    # Outputs the String name of the page object
    def __str__(self):
        return self.title

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')