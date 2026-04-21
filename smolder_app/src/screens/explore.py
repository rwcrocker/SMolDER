from __future__ import annotations

import base64
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from shiny import reactive, render, req, ui
from shinywidgets import output_widget, render_widget

from data.db import query_fda_drugs, query_indications, query_targets

_PROP_LABELS = {
    "mol_weight": "Molecular Weight (Da)",
    "logp": "LogP",
    "tpsa": "TPSA (Å²)",
    "hbd": "H-Bond Donors",
    "hba": "H-Bond Acceptors",
    "arom_c": "Aromatic Carbons",
    "rot_bonds": "Rotatable Bonds",
}

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

page_ui = ui.page_fluid(
    ui.navset_tab(
        # ── Tab 1: Structures ──────────────────────────────────────────────
        ui.nav_panel(
            "Structures",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_text("struct_search", "Search drug name", placeholder="e.g. ibuprofen"),
                    ui.input_action_button("struct_search_btn", "Search", class_="btn-primary w-100"),
                    ui.hr(),
                    ui.output_ui("selected_drug_info"),
                ),
                ui.output_data_frame("drug_table"),
                ui.output_ui("structure_svg"),
            ),
        ),
        # ── Tab 2: Properties ──────────────────────────────────────────────
        ui.nav_panel(
            "Properties",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_select(
                        "prop_x", "X axis",
                        choices=list(_PROP_LABELS.keys()),
                        selected="mol_weight",
                    ),
                    ui.input_select(
                        "prop_y", "Y axis",
                        choices=list(_PROP_LABELS.keys()),
                        selected="logp",
                    ),
                    ui.input_select(
                        "prop_hist", "Histogram property",
                        choices=list(_PROP_LABELS.keys()),
                        selected="mol_weight",
                    ),
                ),
                output_widget("scatter_plot"),
                output_widget("hist_plot"),
            ),
        ),
        # ── Tab 3: Targets & Indications ───────────────────────────────────
        ui.nav_panel(
            "Targets & Indications",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_radio_buttons(
                        "assoc_view", "Show",
                        choices=["Targets", "Indications"],
                        selected="Targets",
                    ),
                    ui.input_numeric("assoc_top_n", "Top N (by drug count)", value=20, min=5, max=100),
                    ui.input_switch("moa_only", "MoA targets only", value=True),
                ),
                output_widget("association_chart"),
            ),
        ),
        # ── Tab 4: Timeline ────────────────────────────────────────────────
        ui.nav_panel(
            "Timeline",
            output_widget("timeline_chart"),
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_select("timeline_year", "Filter to year (optional)", choices=["All"], selected="All"),
                ),
                ui.output_data_frame("timeline_drug_table"),
            ),
        ),
    )
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _smiles_to_svg(smiles: str, width: int = 350, height: int = 250) -> str | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.drawOptions().addStereoAnnotation = True
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()


def _approval_decade(year: float) -> str:
    if pd.isna(year):
        return "Unknown"
    decade = int(year // 10) * 10
    return f"{decade}s"


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def server(input, output, session):

    # ── Shared data ────────────────────────────────────────────────────────

    @reactive.calc
    def drugs():
        return query_fda_drugs()

    @reactive.calc
    def targets():
        return query_targets()

    @reactive.calc
    def indications():
        return query_indications()

    # ── Structures tab ─────────────────────────────────────────────────────

    @reactive.calc
    def filtered_drugs():
        df = drugs()
        term = input.struct_search().strip().lower()
        if term:
            df = df[df["name"].str.lower().str.contains(term, na=False)]
        return df.reset_index(drop=True)

    @render.data_frame
    def drug_table():
        df = filtered_drugs()[["name", "mol_weight", "logp", "tpsa", "approval_year"]]
        df = df.rename(columns={
            "name": "Drug",
            "mol_weight": "MW (Da)",
            "logp": "LogP",
            "tpsa": "TPSA",
            "approval_year": "FDA Approved",
        })
        return render.DataGrid(df, selection_mode="row", height="350px")

    @reactive.calc
    def selected_row():
        sel = drug_table.cell_selection()
        rows = sel.get("rows", []) if sel else []
        if not rows:
            return None
        return filtered_drugs().iloc[rows[0]]

    @render.ui
    def structure_svg():
        row = selected_row()
        if row is None:
            return ui.p("Select a drug above to view its structure.", class_="text-muted")
        svg = _smiles_to_svg(row["smiles"])
        if svg is None:
            return ui.p("Could not render structure.", class_="text-warning")
        return ui.HTML(svg)

    @render.ui
    def selected_drug_info():
        row = selected_row()
        if row is None:
            return ui.p("")
        return ui.div(
            ui.strong(row["name"]),
            ui.br(),
            ui.small(f"MW: {row['mol_weight']:.1f} | LogP: {row['logp']:.2f}"),
            ui.br(),
            ui.small(f"TPSA: {row['tpsa']:.1f} | HBD: {int(row['hbd'])} | HBA: {int(row['hba'])}"),
            ui.br(),
            ui.small(f"FDA approved: {int(row['approval_year']) if not pd.isna(row['approval_year']) else 'N/A'}"),
        )

    # ── Properties tab ─────────────────────────────────────────────────────

    @render_widget
    def scatter_plot():
        df = drugs().copy()
        df["decade"] = df["approval_year"].apply(_approval_decade)
        x, y = input.prop_x(), input.prop_y()
        fig = px.scatter(
            df,
            x=x,
            y=y,
            color="decade",
            hover_name="name",
            labels=_PROP_LABELS,
            title=f"{_PROP_LABELS[y]} vs {_PROP_LABELS[x]}",
            opacity=0.6,
            template="plotly_white",
        )
        fig.update_layout(height=400)
        return fig

    @render_widget
    def hist_plot():
        df = drugs()
        prop = input.prop_hist()
        fig = px.histogram(
            df,
            x=prop,
            nbins=50,
            labels=_PROP_LABELS,
            title=f"Distribution of {_PROP_LABELS[prop]}",
            template="plotly_white",
            color_discrete_sequence=["#4e79a7"],
        )
        fig.update_layout(height=300)
        return fig

    # ── Targets & Indications tab ──────────────────────────────────────────

    @render_widget
    def association_chart():
        view = input.assoc_view()
        n = input.assoc_top_n()

        if view == "Targets":
            df = targets()
            if input.moa_only():
                df = df[df["is_moa"]]
            counts = (
                df.groupby(["target_name", "target_class"])["drug_name"]
                .nunique()
                .reset_index(name="drug_count")
                .sort_values("drug_count", ascending=False)
                .head(n)
            )
            fig = px.bar(
                counts,
                x="drug_count",
                y="target_name",
                color="target_class",
                orientation="h",
                labels={"drug_count": "# FDA Drugs", "target_name": "Target", "target_class": "Class"},
                title=f"Top {n} Targets by Drug Count",
                template="plotly_white",
            )
        else:
            df = indications()
            counts = (
                df.groupby(["indication", "indication_type"])["drug_name"]
                .nunique()
                .reset_index(name="drug_count")
                .sort_values("drug_count", ascending=False)
                .head(n)
            )
            fig = px.bar(
                counts,
                x="drug_count",
                y="indication",
                color="indication_type",
                orientation="h",
                labels={"drug_count": "# FDA Drugs", "indication": "Indication", "indication_type": "Type"},
                title=f"Top {n} Indications by Drug Count",
                template="plotly_white",
            )

        fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
        return fig

    # ── Timeline tab ───────────────────────────────────────────────────────

    @render_widget
    def timeline_chart():
        df = drugs()
        yearly = (
            df.dropna(subset=["approval_year"])
            .groupby("approval_year")
            .size()
            .reset_index(name="count")
        )
        yearly["approval_year"] = yearly["approval_year"].astype(int)
        fig = px.bar(
            yearly,
            x="approval_year",
            y="count",
            labels={"approval_year": "Year", "count": "FDA Approvals"},
            title="FDA Small Molecule Drug Approvals by Year",
            template="plotly_white",
            color_discrete_sequence=["#4e79a7"],
        )
        fig.update_layout(height=400, bargap=0.1)
        return fig

    @reactive.effect
    def _populate_year_choices():
        df = drugs()
        years = sorted(df["approval_year"].dropna().astype(int).unique(), reverse=True)
        ui.update_select("timeline_year", choices=["All"] + [str(y) for y in years])

    @render.data_frame
    def timeline_drug_table():
        df = drugs()
        sel = input.timeline_year()
        if sel != "All":
            df = df[df["approval_year"] == int(sel)]
        else:
            df = df.head(0)
        cols = df[["name", "mol_weight", "logp", "tpsa", "approval_date"]].rename(columns={
            "name": "Drug",
            "mol_weight": "MW (Da)",
            "logp": "LogP",
            "tpsa": "TPSA",
            "approval_date": "Approval Date",
        })
        return render.DataGrid(cols, height="200px")
