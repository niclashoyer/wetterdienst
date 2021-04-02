# -*- coding: utf-8 -*-
# Copyright (c) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE for more info.
"""
Wetterdienst UI layout.
"""
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from wetterdienst.ui.layout.observations_germany import dashboard_layout


def get_about_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(html.P("About Wetterdienst UI")),
            dbc.ModalBody(
                dcc.Markdown(
                    """
                        Wetterdienst UI is a Dash user interface on top of Wetterdienst.

                        **Resources**:
                        - https://wetterdienst.readthedocs.io/en/latest/overview.html
                        - https://github.com/earthobservations/wetterdienst
                                    """
                )
            ),
            dbc.ModalFooter(dbc.Button("Close", id="close-about", className="ml-auto")),
        ],
        id="modal-about",
        is_open=False,
        centered=True,
        autoFocus=True,
        size="lg",
        keyboard=True,
        fade=True,
        backdrop=True,
    )


def get_app_layout():
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(
                [
                    html.H1("Wetterdienst UI"),
                    # html.P("Hello world"),
                    dbc.Navbar(
                        [dbc.NavLink("About", id="open-about")],
                        id="navbar",
                        style={"_align-self": "flex-end", "_float": "right"},
                    ),
                    get_about_modal(),
                ],
                className="row flex-display",
                style={"justify-content": "space-between", "_margin-bottom": "25px"},
            ),
            dashboard_layout(),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
