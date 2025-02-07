from pathlib import Path
import json
import os
img_data_folder = Path("/root/mount/MapGPT/demo/baseline_website/baseline/vis")

img_write_data_folder = Path("/root/mount/MapGPT/demo/baseline_website/baseline/vis2")

for trial_path in img_data_folder.glob('*.jsonl'):
    trial_name = trial_path.stem
    print(trial_name)
    with open(trial_path, 'r') as f:
        for trial in f.readlines():
            trial = json.loads(trial)
            for id, img_path in trial.items():
                new_img_path = '/'.join(img_path.split('/')[-3:])
                new_img_path = 'images/' + new_img_path
                new_img_path = Path(new_img_path)

                absolute_img_path = Path('/root/mount/MapGPT/demo/baseline_website/baseline') / new_img_path
                absolute_img_path.parent.mkdir(parents=True, exist_ok=True)
                # copy image to new location
                os.system(f"cp {img_path} /root/mount/MapGPT/demo/baseline_website/baseline/{new_img_path}")

                trial[id] = str(new_img_path)
            with open(img_write_data_folder / f'{trial_name}.jsonl', 'a') as f:
                f.write(json.dumps(trial) + '\n')
    #     break
    # break