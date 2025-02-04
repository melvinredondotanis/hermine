from dotenv import dotenv_values

from app.docker_utils import app

config = dotenv_values(".env")


def main():
    app.run(
        debug=config["DEBUG"],
        host=config["HOST"],
        port=config["PORT"]
    )


if __name__ == "__main__":
    main()
