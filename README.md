# Sorting Algorithms Animations

This is a collection of animations for some sorting algorithms.

It uses pygame to visualize the algorithms. The animation can be exported to MP4 and GIF by setting `output_video` to `True` when the `Sorter` instance is created.

Current list of algorithms (with a brief explanation of how it works):
- Bubble sort (swap consecutive numbers if not in the correct order)
- ~Shell sort (bubble sort with variable interval)~
- Insertion sort (insert each value after the last number smaller than it)
- Radix LSD sort (for each order of magnitude (1,10,100,...), put each value in a bucket corresponding to its digit for this order)
- Merge sort (recursively split the list, then from the bottom up, rejoin and sort each halves)
- Quick sort (pick a pivot, put values smaller than the pivot before and the others after, apply recursively on each side)

## Disclaimer

I wouldn't recommend trying to sort large lists since:
1. the window's size depends on the size of the list
2. when exporting the videos, each frame is saved in a temporary folder. The larger the list, the longer the video, and the more images will are saved

## Requirements

- Python 3 or higher
- Python modules: `pygame`
- `ffmpeg` to export the videos
