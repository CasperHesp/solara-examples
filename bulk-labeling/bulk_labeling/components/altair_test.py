import json
import pandas as pd
import altair as alt
import solara
from datetime import datetime, timedelta

# Load the JSON file
file_path = "transcript_test.json"
with open(file_path, "r") as file:
    transcript_data = json.load(file)

# Extract transcript entries
transcripts = transcript_data["transcripts"]

# Convert timestamps to seconds
def time_to_seconds(time_str):
    t = datetime.strptime(time_str, "%H:%M:%S")
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second).total_seconds()

def seconds_to_time(seconds):
    return str(timedelta(seconds=int(seconds)))

# Convert transcript to a DataFrame
df = pd.DataFrame(transcripts)
df = df.dropna(subset=["timestamp", "dialogue"])  # Drop entries without timestamps or dialogue
df["timestamp_seconds"] = df["timestamp"].apply(time_to_seconds)
df.sort_values("timestamp_seconds", inplace=True)

# Define time window parameters
window_size = 120  # 2 minutes in seconds
total_duration = 54 * 60 + 53  # 54 minutes and 53 seconds

# Create windows
windows = []
speakers = set(df["role"])  # Unique speakers

for start_time in range(0, total_duration, window_size):
    end_time = start_time + window_size
    window_df = df[(df["timestamp_seconds"] >= start_time) & (df["timestamp_seconds"] < end_time)]
    
    window_summary = {
        "start_time": seconds_to_time(start_time),
        "end_time": seconds_to_time(end_time),
        "num_lines": len(window_df),
        "total_words": int(window_df["dialogue"].str.split().str.len().sum()) if not window_df.empty else 0,
        "num_speakers": len(window_df["role"].unique()),
        "full_dialogue": " ".join(window_df["dialogue"].tolist()) if not window_df.empty else ""
    }
    
    # Add per-speaker stats
    for speaker in speakers:
        speaker_df = window_df[window_df["role"] == speaker]
        window_summary[f"{speaker}_num_lines"] = len(speaker_df)
        window_summary[f"{speaker}_word_count"] = int(speaker_df["dialogue"].str.split().str.len().sum()) if not speaker_df.empty else 0
    
    windows.append(window_summary)

# Convert to DataFrame
result_df = pd.DataFrame(windows)

selected_datum = solara.reactive(None)

@solara.component
def altairPage():
    def on_click(datum):
        selected_datum.value = datum

    melted_words = result_df.melt(
        id_vars=["start_time", "end_time"],
        value_vars=[col for col in result_df.columns if col.endswith("_word_count")],
        var_name="speaker",
        value_name="word_count",
    )
    melted_words["speaker"] = melted_words["speaker"].str.replace("_word_count", "")

    chart_words = (
        alt.Chart(melted_words, title="Speaker Word Count Over Time")
        .mark_rect()
        .encode(
            alt.X("start_time:N", title="Transcript Time Bin", sort=None),
            alt.Y("speaker:N", title="Speaker Name"),
            alt.Color("word_count:Q", title="Number of Words"),
            tooltip=[
                alt.Tooltip("start_time", title="Start Time"),
                alt.Tooltip("end_time", title="End Time"),
                alt.Tooltip("speaker", title="Speaker"),
                alt.Tooltip("word_count", title="Words Spoken"),
            ],
        )
        .configure_view(step=13, strokeWidth=0)
        .configure_axis(domain=False)
        .properties(width="container")
    )

    with solara.Card("Speaker Word Count Heatmap"):
        solara.AltairChart(chart_words, on_click=on_click)

altairPage()
