from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Cookbook(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publish_date = models.DateField()
    edition = models.CharField(max_length=20)

    
    def __str__(self):
        return f"'{self.title}' by {self.author}"
