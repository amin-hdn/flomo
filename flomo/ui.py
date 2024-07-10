import datetime
import sys
import threading
import time

import blessed
from rich.align import Align
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

import flomo.helpers as helpers

class UI:
    def __init__(
        self, status: int, tag: str, name: str, chilling_time: int | None = None
    ):
        self.tag = f"#{tag}"
        self.name = name
        self.status = status

        self.chilling_time = round(chilling_time) if chilling_time else None
        self.stopwatch = 0
        self.close_live_panel = False

        self.title = "Flomo - " + ("FLOWING" if self.status == 0 else "CHILLIN")
        self.border_style = "bold blue" if self.status == 0 else "bold red"

        self.terminal = blessed.Terminal()

    def generate_panel(self):
        stuff = f"{self.name}\n[grey70]{self.tag}[/grey70]\n\n{helpers.format_time(
            self.stopwatch if (self.status == 0) else self.chilling_time or 0)}\n\n\\[q] - {'break' if self.status == 0 else 'skip?'}    [Ctrl+C] - quit"
        content = Text.from_markup(stuff, justify="center", style="yellow")
        return Align.center(
            Panel(
                content,
                expand=False,
                title=self.title,
                border_style=self.border_style,
                title_align="center",
                padding=(1, 2),
            ),
            vertical="middle",
            height=self.terminal.height,
        )

    def show_live_panel(self):
        with Live(self.generate_panel(), refresh_per_second=4, screen=True) as _live:
            while not self.close_live_panel:
                time.sleep(1)
                if self.status == 0:
                    self.stopwatch += 1
                elif self.status == 1 and self.chilling_time:
                    if not (self.chilling_time > 1):
                        break
                    self.chilling_time -= 1
                _live.update(self.generate_panel())

    def get_input(self):
        with self.terminal.cbreak(), self.terminal.hidden_cursor():
            return self.terminal.inkey().lower()


def main(tag: str, name: str, session_id: float):
    #TODO: Do something with the Terminal close issue
    try:
        while True:
            play_sound_thread = threading.Thread(target=helpers.play_sound, daemon=True)
            play_sound_thread.start()

            flowing_ui = UI(0, tag, name)
            flowing_panel_thread = threading.Thread(
                target=flowing_ui.show_live_panel, daemon=True
            )
            flowing_panel_thread.start()

            inp = ""
            while flowing_ui.stopwatch == 0 or not (
                flowing_ui.stopwatch != 0 and inp == "q"
            ):
                inp = flowing_ui.get_input()

            chilling_time = flowing_ui.stopwatch / 5

            flowing_ui.close_live_panel = True
            flowing_panel_thread.join()
            play_sound_thread.join()

            del flowing_ui

            chilling_ui = UI(1, tag, name, int(chilling_time))
            chilling_ui.show_live_panel()
            # chilling_panel_thread = threading.Thread(
            #     target=chilling_ui.show_live_panel, daemon=True)
            # chilling_panel_thread.start()

            # while True:
            #     if chilling_ui.chilling_time == 1:
            #         break
            #     helpers.message_log(str(chilling_ui.chilling_time))
            #     inp = chilling_ui.get_input()
            #     if inp == "q":
            #         break

            chilling_ui.close_live_panel = True
            # chilling_panel_thread.join()

            del chilling_ui
    except (KeyboardInterrupt, Exception) as e:
        if "flowing_ui" in locals() and flowing_ui is not None:
            flowing_ui.close_live_panel = True
        if "chilling_ui" in locals() and chilling_ui is not None:
            chilling_ui.close_live_panel = True
        if "flowing_panel_thread" in locals() and flowing_panel_thread.is_alive():
            flowing_panel_thread.join()
        if "play_sound_thread" in locals() and play_sound_thread.is_alive():
            play_sound_thread.join()
        # if 'chilling_panel_thread' in locals() and chilling_panel_thread.is_alive():
        #     chilling_panel_thread.join()

        if isinstance(e, Exception):
            helpers.message_log(f"{datetime.datetime.now()} - Error: {e}")
    finally:
        helpers.update_session(session_id)
        sys.exit()
