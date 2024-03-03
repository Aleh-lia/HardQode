from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from rest_framework.authtoken.admin import User

from mysite.models import *
from rest_framework import serializers, viewsets
from django.db.models import Count, Avg, F


# Create your views here.
def assign_user_to_group(user, product):
    # Получаем все группы для данного продукта
    groups = list(Group.objects.filter(product=product).order_by('users__count'))

    for i in range(len(groups) - 1):
        # Если разница между количеством участников в этой группе и следующей группе больше 1,
        # добавляем пользователя в эту группу
        if groups[i + 1].users.count() - groups[i].users.count() > 1:
            if groups[i].users.count() < groups[i].max_users:
                groups[i].users.add(user)
                return

    # Если все группы имеют одинаковое количество участников или разница между количеством участников
    # в любых двух группах не превышает 1, добавляем пользователя в любую группу, которая еще не достигла
    # своего максимального значения
    for group in groups:
        if group.users.count() < group.max_users:
            group.users.add(user)
            return

    # Если все группы достигли своего максимального значения, создаем новую группу и добавляем пользователя в эту группу
    new_group = Group.objects.create(name=f'Group {len(groups) + 1}',
                                     product=product, min_users=1, max_users=10)
    new_group.users.add(user)


class ProductSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'start_date_time', 'cost', 'creator', 'lessons_count']

    def get_lessons_count(self, obj):
        return Lesson.objects.filter(product=obj).count()


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'video_link', 'product']


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        product_id = self.kwargs['product_id']

        # Проверяем, есть ли у пользователя доступ к продукту
        if not AccessToProduct.objects.filter(user=user, product_id=product_id).exists():
            raise PermissionDenied('У вас нет доступа к этому продукту.')

        return queryset.filter(product_id=product_id)


# реализовать API для отображения статистики по продуктам.
class ProductStatsSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()
    groups_fill_percentage = serializers.SerializerMethodField()
    product_purchase_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'start_date_time', 'cost', 'creator',
                  'students_count', 'groups_fill_percentage', 'product_purchase_percentage']

    def get_students_count(self, obj):
        return AccessToProduct.objects.filter(product=obj).count()

    def get_groups_fill_percentage(self, obj):
        groups = Group.objects.filter(product=obj)
        total_users = sum(group.users.count() for group in groups)
        total_capacity = sum(group.max_users for group in groups)
        return (total_users / total_capacity) * 100 if total_capacity > 0 else 0

    def get_product_purchase_percentage(self, obj):
        total_users = User.objects.count()
        product_users = AccessToProduct.objects.filter(product=obj).count()
        return (product_users / total_users) * 100 if total_users > 0 else 0

class ProductStatsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductStatsSerializer