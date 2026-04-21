from shiny import ui

page_ui = ui.page_fluid(
    ui.h1("Small Molecule Drug Explorer (SMolDER)"),
    ui.hr(),
    ui.p("Welcome to SMolDER, the interactive small molecule drug exploration app."),

    ui.h2("Data"),
    ui.hr(),
    ui.p("The data in the SMolDER app comes from DrugCentral and PubChem."),

    ui.h2("App"),
    ui.hr(),
    ui.p("The SMolDER app was made using Python Shiny.")


)