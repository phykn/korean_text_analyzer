import pandas as pd
import altair as alt
from typing import List


def plot_count(
    word: List[str],
    count: List[int],
    num: int=10
) -> alt.Chart:
    source = pd.DataFrame(
        data = {"word": word, "count": count}
    ).iloc[:num]

    fig = alt.Chart(source, title=f"Top {num}").mark_bar(color='#EA4A54').encode(
        x = alt.X("count:Q", title="개수"),
        y = alt.Y("word:N", title=None, sort="-x"),
        tooltip = [
            alt.Tooltip("word", title="word"),
            alt.Tooltip("count", title="count")
        ]
    ).properties(
        width=600,
        height=600
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20
    )
    return fig