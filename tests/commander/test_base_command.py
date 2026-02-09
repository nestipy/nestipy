import click

from nestipy.commander.abstract import BaseCommand


class DummyCommand(BaseCommand):
    async def run(self):
        return "ok"


def test_base_command_init_parsing():
    cmd = DummyCommand()
    cmd.init(("arg1", "--foo", "bar", "-x", "1", "--flag", "--name=bob"))

    assert cmd.get_arg(0) == "arg1"
    assert cmd.get_opt("foo") == "bar"
    assert cmd.get_opt("x") == "1"
    assert cmd.get_opt("flag") is True
    assert cmd.get_opt("name") == "bob"


def test_base_command_get_arg_default():
    cmd = DummyCommand()
    cmd.init(("only",))
    assert cmd.get_arg(10, "missing") == "missing"


def test_base_command_info_error_calls_click(monkeypatch):
    calls = []

    def fake_secho(message, **kwargs):
        calls.append((message, kwargs))

    monkeypatch.setattr(click, "secho", fake_secho)

    DummyCommand.info("info")
    DummyCommand.error("error")
    DummyCommand.warning("warn")
    DummyCommand.success("ok")

    assert calls[0][1].get("fg") == "green"
    assert calls[1][1].get("fg") == "red"
    assert calls[2][1].get("fg") == "orange"
    assert calls[3][1].get("fg") == "green"
    assert calls[3][1].get("bold") is True
