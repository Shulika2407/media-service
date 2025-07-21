from django.apps import AppConfig


class CustomerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customer"

    def ready(self):
        # Імпортуємо ваші сигнали тут, щоб вони реєструвалися при запуску додатку
        import customer.signals
