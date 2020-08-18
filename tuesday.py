import datetime
import subprocess

CONTENT = """\
<!DOCTYPE html>
<html lang="en-us">
<meta charset="utf-8">
<title>Is it Tuesday?</title>
<body style="margin: auto; width: 10%;">
<h1>{tuesday}</h1>
"""


def is_tuesday():
    weekday = subprocess.run(
        ["date", "+%w"],
        env={"TZ": "America/Los_Angeles"},
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    return weekday == b"2\n"


def application(env, start_response):
    start_response("200 OK", [("Content-Type", "text/html")])
    res = CONTENT.format(tuesday="Yes!" if is_tuesday() else "No")
    return [bytes(res, encoding="utf-8")]
