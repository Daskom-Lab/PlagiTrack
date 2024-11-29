# #PlagiTrack

---

## Requirements

- `thefuzz` and `rapidfuzz` for comparing tokens by ratios.
- `copydetect` for comparing files structurally.

## Installation and Usage

1. Ensure you have a Python installed on your device.

> It could be any version, but for safety precautions, around version `3.10` to `3.13` should be more than enough...

2. Install all the necessary dependencies:

> `pip install -r requirements.txt`

3. Prepare some files (locally), independent from any file formats.

> Make sure at least TWO (2) files are available on your current directory or anywhere else, since the comparison took at least TWO (2) files, or more...

4. Modifying the `TRANSFORMATION_FACTOR` or `LEAST_PLAGIARISM` variable inside the `CONFIGURATIONS.cfg` file.

> Defaults both to: `0.8` and `30.00%` respectively. See inside of the configuration file for more detailed explanation on what to modify...

5. Fill in the file path(s) into the source code, located at `./static/src/PlagCheck_NUE.py`, seek to a variable named `Programs` (currently sitting at line `77`), and insert all of your necessities.

6. Run the program, and wait for the comparison and listing ended. After that, go to the outer directory for `PlagiTrack` and see the results on a separate folder, namely `./caches`.

## Limitations

1. Currently, the plagiarism checking is available for local devices only, and waiting to be integrated into the main website for `PlagiTrack` in the future by `@tak2tahu`.

2. Current algorithm for plagiarism checking (tokenizations and comparing for each tokens by ratios) by `@EintsWaveX` is now limited to only tokens of each code program, listed inside the variable `Progam` (see **Installation and Usage, No. 5**), and from `@tak2hu` will use the algorithm for comparing files by structures/similarities, using `copydetect` library.

3. The plagiarism checking result is ranging between `0.00%` to `100.00%`, but for the sake of "NOT GETTING ALMOST EVERY PRACTITIONERS INTO PLAGIARISM" (since the C-syntax is just always like that), `@EintsWaveX` use the `Transformation Formula` to reduces mid-range scores without significantly altering extreme values (high or low scores).

> See https://chatgpt.com/share/674a2c4e-dffc-800b-ad66-976ccb00bb3b for more detailed information.

---
