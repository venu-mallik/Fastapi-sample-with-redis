from pydantic import BaseSettings


class Settings(BaseSettings):
    '''
    should be loaded from a .env file for production
    '''
    production: str = 'false'
    app_name: str = "Vetty Api"
    db_url: str = "sqlite:///./sql_app.db"
    redis_host: str = "redis-11249.c266.us-east-1-3.ec2.cloud.redislabs.com"
    redis_port: str = 11249
    redis_password: str = ""


settings = Settings()
