# streamlit run view_output.py
import streamlit as st
from pathlib import Path

from collections import defaultdict
import json
import math
import pandas as pd

# Main folder
output_folder = Path("baseline")

gpt_dir = output_folder / "gpt"
log_dir = output_folder / "logs"
maps_dir = output_folder / "maps"
vis_dir = output_folder / "vis2"
traj_dir = output_folder / "traj"

# get all available scenes
available_scenes = [f"{p.stem}" for p in (gpt_dir / "in").glob("*.jsonl")]

# load metrics
with open(log_dir / "detail_metrics.json", "r") as f:
    metrics = json.load(f)

# convert to dataframe and set index
metrics = pd.DataFrame(metrics)
metrics = metrics.set_index("env_ids")

# order based on available scenes
metrics = metrics.loc[available_scenes]

# view all failed scenes
view_failed = st.sidebar.checkbox("Failed Scenes Only", True)
if view_failed:
    available_scenes = metrics[metrics["success"] == 0].index.tolist()
    metrics = metrics[metrics["success"] == 0]

default_scene = st.query_params.get("scene", available_scenes[0]).strip()

if default_scene not in available_scenes:
    default_scene = available_scenes[0]

# select scene
scene = st.sidebar.selectbox("Scene", available_scenes, available_scenes.index(default_scene))

# select scene folders
gpt_in = gpt_dir / "in" / f"{scene}.jsonl"
gpt_out = gpt_dir / "out" / f"{scene}.jsonl"
vis = vis_dir / f"{scene}.jsonl"
maps = list((maps_dir / f"{scene}").glob("*.png"))

# max steps
max_steps = len(maps)
# select step
step = st.sidebar.number_input("Step", 1, max_steps, 1)


# load gpt input
with open(gpt_in, "r") as f:
    gpt_in_data = f.readlines()[step - 1]
    gpt_in_data = json.loads(gpt_in_data)

# load gpt output
with open(gpt_out, "r") as f:
    gpt_out_data = f.readlines()[step - 1]
    gpt_out_data = json.loads(gpt_out_data)

# load images
with open(vis, "r") as f:
    vis_data = f.readlines()[step - 1]
    vis_data = json.loads(vis_data)

# show instruction
st.write("instruction: ", gpt_in_data["instruction"])

# show Map
st.write("Map")
map_path = maps_dir / f"{scene}" / f"step_{step}.png"
st.image(str(map_path), caption=f"Step {step}")

# show images
st.write("Images")
# sort by dic key
with st.container():
    item_per_row = 2
    columns_count = math.ceil(len(vis_data) / item_per_row)
    for i in range(columns_count):
        column = st.columns(item_per_row)
        for j in range(item_per_row):
            idx = i * item_per_row + j
            if idx >= len(vis_data):  # ignore the last image (map)
                break
            key, img = list(vis_data.items())[idx]
            if not img:
                continue
            img = Path("baseline") / img
            column[j].image(img, width=350, caption=f"Node {key}")

# show gpt input and output
st.write("GPT Input")
st.json(gpt_in_data)
st.write("GPT Output")
st.json(gpt_out_data)

# show target trajectory
st.write("Target Trajectory")
st.image(str(traj_dir / f"{scene}.png"), caption="Target Trajectory")

# show metrics
st.write("Metrics")

# show detailed metrics
show_detailed_metrics = st.checkbox("Show Detailed Metrics")
if not show_detailed_metrics:
    metrics = metrics[
        [
            "nav_error",
            "success",
            "oracle_success",
            "spl",
        ]
    ]


metrics_df = pd.DataFrame(metrics)

st.write(metrics_df)

# calculate the mean success
st.write("Mean Success Rate: ", metrics_df["success"].mean())

# show config too

# load config
with open(log_dir / "config.json", "r") as f:
    config = json.load(f)

st.write("Config")
st.json(config)