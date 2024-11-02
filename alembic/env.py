from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# O'z model faylingizdan Base ni import qiling
from app.models import Base  # o'zgartiring

# konfiguratsiya faylidan olingan sozlamalar
config = context.config

# Logging sozlamalari
fileConfig(config.config_file_name)

# `target_metadata` ni belgilash
target_metadata = Base.metadata  # O'zgartiring

def run_migrations_offline():
    """Offline rejimda migratsiyalarni bajarish."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Online rejimda migratsiyalarni bajarish."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
