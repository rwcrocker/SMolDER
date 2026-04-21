from shiny import App, ui
from shinyswatch import theme
from screens import homepage, explore

smolder_ui = ui.page_navbar(
    ui.nav_panel("About", homepage.page_ui),
    ui.nav_panel("Explore", explore.page_ui),
    ui.nav_panel("Contact", ui.page_fluid()),
    title="SMolDER",
    theme=theme.cosmo(),
    navbar_options=ui.navbar_options(theme="dark"),
)


def smolder_server(input, output, session):
    explore.server(input, output, session)


app = App(smolder_ui, smolder_server)
