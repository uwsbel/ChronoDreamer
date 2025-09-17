#!/bin/bash

for i in $(seq 1 20); do
    folder="test_$(date +%Y%m%d_%H%M%S)_$i"
    mkdir -p "$folder/sensor_img"

    # Run Python script
    python3 jz_robotiq_push_ou.py --output-dir "$folder"

    # Enter the sensor_img folder, run mogrify, then return
    if [ -d "$folder/sensor_img" ]; then
        (
            cd "$folder/sensor_img" || exit 1
            mogrify -format jpg -quality 80 *.png
            rm *.png
        )
    fi
done

