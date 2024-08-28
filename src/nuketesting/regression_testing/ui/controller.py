"""Controller for the regression test user interface."""

import nuke
from nukescripts import PythonPanel, registerPanel

from nuketesting.regression_testing.ui.ui import RegressionTestPanel


class _WidgetKnob:
    """Knob for QT widgets inside nuke panels.

    This class conforms to nukes call stack. No useful features.
    """

    @staticmethod
    def makeUI() -> RegressionTestPanel:  # noqa: N802 Name is dictated by foundry
        """Instantiate the panel.

        Called by the nuke panel creation process. Needs to be called ``makeUI``.
        """
        return RegressionTestPanel()


def register_in_nuke() -> None:
    """Register the user interface inside nuke."""
    name = "Regression Test Panel"
    panel_id = "nuketesting.ui.regression"

    class NukePanel(PythonPanel):
        """Implementation of the nuke python panel for the regression panel."""

        def __init__(self):
            super().__init__(name, panel_id)
            main_package, *sub_packages = _WidgetKnob.__module__.split(".")
            knob = nuke.PyCustom_Knob(
                name, "", f"__import__(\"{main_package}\").{'.'.join(sub_packages)}.{_WidgetKnob.__name__}()"
            )
            self.addKnob(knob)

    def create_and_add_panel() -> NukePanel:
        """Instantiate the panel."""
        return NukePanel().addToPane()

    menu = nuke.menu("Pane")
    menu.addCommand(name, create_and_add_panel)
    registerPanel(panel_id, create_and_add_panel)
