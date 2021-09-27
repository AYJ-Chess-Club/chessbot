# AYJ chess club discord bot

[![Build](https://github.com/AYJ-Chess-Club/chessbot/actions/workflows/build.yml/badge.svg)](https://github.com/AYJ-Chess-Club/chessbot/actions/workflows/build.yml)
![](https://img.shields.io/discord/777192115951763468?color=blue)

| Command          | Arguments                               | Permissions |
| ---------------- | --------------------------------------- | ----------- |
| `+dump`          | `[user]`                                | None        |
| `+help`          | `[command name]`                        | None        |
| `+me`            | N/A                                     | None        |
| `+verify`        | `<first name>` `<last name>` `<school>` | None        |
| `+setinvitefrom` | `<person name>`                         | Admin       |

\*Note [] means optional, <> means required

## Contributing

Clone the repo 

```shell
$ git clone git@github.com:AYJ-Chess-Club/chessbot.git
```

Create your virtual environment

```shell
$ python -m venv venv
$ source venv/bin/activate
```

Install dependencies

```shell
$ pip install -r requirements.txt
```

Create the `.env` file

```shell
$ touch .env
```

Place the bot token into the env file:

```
token=tokenhere
```

Run

```shell
$ python main.py
```
