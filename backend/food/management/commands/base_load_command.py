import json
from django.core.management.base import BaseCommand


class BaseLoadCommand(BaseCommand):
    model = None  # установить в дочернем классе

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Путь к JSON-файлу'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, encoding='utf-8') as file:
                data = json.load(file)
                created = self.model.objects.bulk_create(
                    (self.model(**item) for item in data),
                    ignore_conflicts=True
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Добавлено {len(created)} объектов из файла "{file_path}"'
                    )
                )
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(
                f'Файл не найден: {file_path}'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Ошибка при обработке файла {file_path}: {e}'
            ))  