#!/usr/bin/env bash

# Loop through every subfolder in the current directory
for dir in */; do
    sensor_dir="${dir}sensor_img"
    if [[ -d "$sensor_dir" ]]; then
        echo "Processing: $sensor_dir"
        (
            cd "$sensor_dir" || { echo "❌ Cannot enter $sensor_dir"; exit 1; }

            ffmpeg -y -framerate 30 -start_number 0 -i "frame_%d.jpg" \
                   -c:v libx264 -pix_fmt yuv420p "video.mp4"

            echo "  ✅ Created: $PWD/video.mp4"
        )
    else
        echo "⚠️  No sensor_img directory in $dir"
    fi
done

