import solara as sl

from bulk_labeling.components.df import DFView, NoEmbs
from bulk_labeling.components.altair_test import altairPage
from bulk_labeling.components.menu import AssignedLabelView, Menu
from bulk_labeling.state import PlotState, State
from bulk_labeling.utils.df import has_df


@sl.component
def NoDF() -> None:
    with sl.Column(align="center"):
        sl.Markdown("# No Data Loaded")
        sl.Markdown("*Please load some data using the sidebar to get started*")


@sl.component
def Page() -> None:
    sl.Title("Process your rushes.")
    # TODO: Why cant i get this view to render?
    AssignedLabelView()
    with sl.Sidebar():
        Menu()
    
    #with sl.Column(align="start"):
    altairPage()
    #if has_df(State.df.value) and PlotState.loading.value:
    #    NoEmbs()
    #elif has_df(State.df.value):
    #    DFView()
    #else:
    #    NoDF()


if __name__ == "__main__":
    Page()
