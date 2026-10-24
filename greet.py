import click


def build_greetings(name: str, times: int) -> list[str]:
    if times < 1:
        raise ValueError("times должно быть не меньше 1")
    return [f"Привет, {name}!" for _ in range(times)]


@click.command()
@click.argument("name")
@click.option("--times", "-t", type=int, default=1, help="Сколько раз поздороваться")
def greet(name, times):
    """Приветствует NAME TIMES раз."""
    try:
        lines = build_greetings(name, times)
    except ValueError as error:
        raise click.BadParameter(str(error), param_hint="--times")
    for line in lines:
        click.echo(line)


if __name__ == "__main__":
    greet()
