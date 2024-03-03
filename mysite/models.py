from django.db import models


class Users(models.Model):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    lastname = models.CharField(max_length=50, null=True, verbose_name="Фамилия")
    firstname = models.CharField(max_length=50, null=True, verbose_name="Имя")
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)


class Product(models.Model):
    name = models.CharField(max_length=100)
    start_date_time = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(Users, on_delete=models.CASCADE)


# доступ к продукту
class AccessToProduct(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Lesson(models.Model):
    name = models.CharField(max_length=100)
    video_link = models.URLField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Group(models.Model):
    name = models.CharField(max_length=100)
    min_users = models.IntegerField()
    max_users = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    users = models.ManyToManyField(Users, through='GroupMembership')


class GroupMembership(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)