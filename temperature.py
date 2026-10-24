import click


def convert_temperature(value: float, unit: str) -> float:
    """unit — единица, в которой задано value: "c" -> результат в °F, "f" -> в °C."""
    if unit == "c":
        return value * 9 / 5 + 32
    if unit == "f":
        return (value - 32) * 5 / 9
    raise ValueError(f"неизвестная единица: {unit}")


@click.command()
@click.option("--value", type=float, required=True, help="Температура")
@click.option("--unit", type=click.Choice(["c", "f"]), required=True,
              help="Единица, в которой задано --value")
def temperature(value, unit):
    """Конвертирует между °C и °F."""
    result = convert_temperature(value, unit)
    if unit == "c":
        click.echo(f"{value:g}°C = {result:.1f}°F")
    else:
        click.echo(f"{value:g}°F = {result:.1f}°C")


if __name__ == "__main__":
    temperature()
