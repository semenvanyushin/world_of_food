from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка подготовленных тегов'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#ff8f1f', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#6cc470', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#b38dd9', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)

        self.stdout.write(self.style.SUCCESS(
            'Загрузка тегов выполнена успешно!'))
