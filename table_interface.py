import time

from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text


console = Console()

table = Table(show_footer=False)
table_centered = Align.center(table)

console.clear()

table.add_column("Date", no_wrap=True)
table.add_column("Transcription")
table.add_column("Cost", no_wrap=True)

table.columns[0].header_style = "bold green"
table.columns[0].style = "green"
table.columns[1].header_style = "bold blue"
table.columns[1].style = "blue"
table.columns[1].footer = "Total"
table.columns[2].header_style = "bold cyan"
table.columns[2].style = "cyan"
table.row_styles = ["none", "dim"]
table.box =  box.SIMPLE_HEAD

with Live(table_centered, console=console, screen=False, refresh_per_second=5):
    time.sleep(2)
    table.add_row("11th March, 8:37pm", "Hey! Hello World.", "$0.0002")
    time.sleep(2)
    table.add_row("11th March, 8:42pm", "SVD is a matrix transformer that's used for...", "$0.01")
    time.sleep(2)
    table.add_row("11th March, 8:54pm", Text("API Error", style="bold red"), "$0.00")

