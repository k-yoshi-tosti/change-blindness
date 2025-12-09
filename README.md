# change-blindness

We made a small script to run an experiment related to change blindness.

A grid of characters is shown for a few seconds, then the screen becomes blank for a certain duration (sometimes 0), then a single character changes.

The user has to click on the character which changed.

Usually, we are always able to see the change when there is no flicker between the two grids. However, even a very short blank delay (as small as 50 milliseconds) can entirely wipe out our short-term visual memory and make us unable to detect the change.

# Usage

Run `python main.py` to launch the main script. At the end of the experiment, the result is saved in a file `data/result{i}.csv` (where i is the smallest integer such that the file does not already exist).

Run `python main.py data/result0.csv` to only show the results without running the experiment again.

Data is saved as a csv file, containing for each iteration `delay success click_delay`.

If needed: `pip install pygame matplotlib`.

# Authors

Inès Bichon & Pablo Rey