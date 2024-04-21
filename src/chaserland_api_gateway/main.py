from chaserland_api_gateway.config.app import app_settings
from chaserland_api_gateway.config.log import log_settings

if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run(
            "app:app",
            host=app_settings.HOST,
            port=app_settings.PORT,
            log_config=log_settings.UVICORN_LOG_CONFIG,
            reload=app_settings.DEBUG,
            reload_dirs=[app_settings.BASE_PATH],
            app_dir=app_settings.BASE_PATH,
            server_header=False,
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e
