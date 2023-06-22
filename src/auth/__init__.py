from dotenv import load_dotenv, find_dotenv


def dotenv_auth():
    """ Load .env file for authentication """
    try:
        load_dotenv(find_dotenv())
    except FileNotFoundError:
        print("\n\nPlease upload your .env file to the local directory\n")