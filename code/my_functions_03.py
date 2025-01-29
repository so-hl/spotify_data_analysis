from IPython.display import display, clear_output
from plotnine import *


def update_plot_feature(df, feature):
    """
    Updates the plot based on the selected feature and its relationship with popularity.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be plotted.
        feature (str): The name of the feature to be plotted on the x-axis.

    Returns:
        None: Displays the plot in the Jupyter notebook.
    """
    clear_output(wait=True)
    plot = (
        ggplot(df, aes(x=feature, y="Popularity"))
        + geom_point(alpha=0.6, color="darkblue")  # Scatter points
        + geom_smooth(method="lm", color="skyblue", se=True)  # Add regression line
        + labs(
            title=f"Relationship between {feature} and Popularity",
            x=feature,
            y="Popularity",
        )
        + theme_minimal()
    )
    display(plot)


def update_plot_playlist(df, region):
    """
    Updates the plot based on the selected region, comparing TikTok Score and Popularity for different playlists.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be plotted.
        region (str): The region to filter the data by, which can be 'Global', 'UK', 'Singapore', or 'USA'.

    Returns:
        None: Displays the plot in the Jupyter notebook.
    """
    clear_output(wait=True)
    filtered_df = df[df["Region"] == region]

    plot = (
        ggplot(filtered_df, aes(x="TikTok_Score", y="Popularity", color="Playlist"))
        + geom_point(alpha=0.6)
        + geom_smooth(method="lm", se=False)
        + labs(
            title=f"Comparing Top50 vs Viral50 ({region})",
            x="TikTok Score",
            y="Popularity",
        )
        + theme_minimal()
    )
    display(plot)
