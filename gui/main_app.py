from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
import threading
import os

from main import AroxiaBot
from aroxia.loader import HotReloader

class TerminalTab(BoxLayout):
    def __init__(self, bot_instance, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.bot = bot_instance
        self.reloader = HotReloader()
        
        self.output = TextInput(readonly=True, background_color=(0,0,0,1), foreground_color=(0,1,0,1), multiline=True)
        self.input = TextInput(multiline=False, size_hint_y=None, height=50)
        self.input.bind(on_text_validate=self.run_command)
        
        self.add_widget(self.output)
        self.add_widget(self.input)
        
        self.output.text = "Aroxia Hotfix Terminal\nType 'help' for commands.\n"

    def run_command(self, instance):
        cmd = self.input.text
        self.input.text = ""
        self.output.text += f"\n> {cmd}\n"
        
        if cmd == "help":
            self.output.text += "Commands: reload <module>, fix <file> <content>, status, clear, gemini <query>\n"
        elif cmd == "clear":
            self.output.text = ""
        elif cmd.startswith("reload "):
            module = cmd.split(" ")[1]
            res = self.reloader.reload_module(module)
            self.output.text += f"{res}\n"
        elif cmd.startswith("gemini "):
            query = cmd[7:]
            if self.bot and self.bot.brain:
                # Run in thread to not block UI
                threading.Thread(target=self._query_gemini, args=(query,)).start()
            else:
                self.output.text += "Bot or Brain not initialized.\n"
        elif cmd == "status":
            self.output.text += f"Bot Status: {'Running' if self.bot else 'Stopped'}\n"
        else:
            self.output.text += "Unknown command.\n"

    def _query_gemini(self, query):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.bot.brain.generate_response(f"[TERMINAL DEBUG] {query}"))
        def update_ui(dt):
            self.output.text += f"Gemini: {response}\n"
        Clock.schedule_once(update_ui)
class AroxiaApp(App):
    def build(self):
        self.bot_token = "8621619489:AAE8JGosFxq1391LraS4NrTboo4MCita2Aw"
        self.bot = None
        self.intel = IntelligenceModule()

        tp = TabbedPanel(do_default_tab=False)

        # Status Tab
        status_tab = TabbedPanelItem(text='Status')
        self.status_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.status_label = Label(text="Bot is Stopped", font_size=20)
        self.sys_monitor = Label(text="CPU: 0% | RAM: 0%", font_size=16, color=(0, 1, 1, 1))
        self.start_btn = Button(text="Start Aroxia", size_hint_y=None, height=100)
        self.start_btn.bind(on_release=self.toggle_bot)

        self.status_layout.add_widget(self.status_label)
        self.status_layout.add_widget(self.sys_monitor)
        self.status_layout.add_widget(self.start_btn)
        status_tab.add_widget(self.status_layout)

        # Terminal Tab
        terminal_tab = TabbedPanelItem(text='Terminal')
        self.terminal = TerminalTab(self.bot)
        terminal_tab.add_widget(self.terminal)

        # Help Tab
        help_tab = TabbedPanelItem(text='Help')
        help_layout = BoxLayout(orientation='vertical', padding=10)
        help_text = ""
        if os.path.exists("config/help.md"):
            with open("config/help.md", "r") as f:
                help_text = f.read()
        help_view = TextInput(text=help_text, readonly=True, multiline=True, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1))
        help_layout.add_widget(help_view)
        help_tab.add_widget(help_layout)

        tp.add_widget(status_tab)
        tp.add_widget(terminal_tab)
        tp.add_widget(help_tab)
        # Update Sys Monitor every 2 seconds
        Clock.schedule_interval(self.update_sys_stats, 2)

        return tp

    def update_sys_stats(self, dt):
        health = self.intel.get_system_health()
        self.sys_monitor.text = f"CPU: {health['cpu_percent']}% | RAM: {health['ram_percent']}% ({health['ram_used_mb']:.1f} MB)"

    def toggle_bot(self, instance):
...

        if not self.bot:
            self.bot = AroxiaBot(self.bot_token)
            threading.Thread(target=self.bot.run, daemon=True).start()
            self.status_label.text = "Bot is Running"
            self.start_btn.text = "Stop Aroxia (Restart Required)"
            self.terminal.bot = self.bot
        else:
            self.status_label.text = "Stop not implemented via UI. Please restart app."

if __name__ == '__main__':
    AroxiaApp().run()
