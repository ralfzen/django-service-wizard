from service_builder.setup_service import setup


if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print('\nExited without changes')
        exit(1)
