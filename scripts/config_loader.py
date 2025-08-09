from decouple import Config, RepositoryEnv

config = Config(repository=RepositoryEnv("/opt/airflow/.env"))
