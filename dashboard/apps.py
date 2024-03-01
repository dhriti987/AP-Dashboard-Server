from django.apps import AppConfig
from threading import Thread


class DashboardConfig(AppConfig):
    """
    Django application configuration for the 'dashboard' app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self) -> None:
        """
        Executes when the Django application is ready.
        Initiates the update of the client token and starts a daemon thread for running the scheduler.
        """
        from dashboard import utilities
        utilities.update_client_token()
        # utilities.dump_data()
        thread = Thread(target=utilities.run_scheduler)
        thread.setDaemon(True)
        thread.start()
