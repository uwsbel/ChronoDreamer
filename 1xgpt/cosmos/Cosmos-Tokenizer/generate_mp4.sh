#!/usr/bin/env bash
set -euo pipefail

FPS=25  # change this if you want a different frame rate

for d in */ ; do
    # Skip if it's not a directory
    [ -d "$d" ] || continue
    echo "Processing directory: $d"

    # 1) sensor_img -> video.mp4
    if [ -d "${d}sensor_img" ]; then
        echo "  Found sensor_img in $d, creating video.mp4"
        ffmpeg -y \
            -framerate "$FPS" \
            -start_number 0 \
            -i "${d}sensor_img/frame_%d.jpg" \
            -c:v libx264 -pix_fmt yuv420p \
            "${d}sensor_img/video.mp4"
    else
        echo "  No sensor_img/ in $d, skipping."
    fi

    # 2) contact_splat -> contact.mp4
    if [ -d "${d}contact_splat" ]; then
        echo "  Found contact_splat in $d, creating contact.mp4"
        ffmpeg -y \
            -framerate "$FPS" \
            -start_number 0 \
            -i "${d}contact_splat/%04d.png" \
            -c:v libx264 -pix_fmt yuv420p \
            "${d}contact_splat/contact.mp4"
    else
        echo "  No contact_splat/ in $d, skipping."
    fi

    echo
done

echo "Done."

