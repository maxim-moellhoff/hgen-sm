<p align="center">
  <img src="assets/images/04_4rect_13.png" alt="Screenshot 3" width="45%"/>
  <img src="assets/images/04_4rect_14.png" alt="Screenshot 4" width="45%"/>
</p>

<p align="center">
  <img src="assets/images/04_6rect_complex_combination.png" alt="Screenshot 3" width="45%"/>
  <img src="assets/images/04_4rect_sol20.png" alt="Screenshot 4" width="45%"/>
</p>

<p align="center">
  <img src="assets/images/04_onshape_01.png" alt="Screenshot 1" width="45%"/>
  <img src="assets/images/04_onshape_04_sol20.png" alt="Screenshot 2" width="34%"/>
</p>

# How it works
The user gives two rectangles as an input, and the program tries to find different ways to connect those two rectangles in way, that is manufacturable. Solutions are generated in two ways. Either by finding the intersection of the two planes and connecting them, or by selecting 2 points from one rectangle and 1 point from the other, and creating an additional tab on that plane.

# How to run it
0. Open the main folder in an IDE or in the console
1. Create a virtual environment
   `python3.13 -m venv ./venv`
2. Activate the virtual environment
   `source venv/bin/activate`
3. Install dependencies (the . at the end is important)
   `pip install -e .`
4. Run the program
   `python -m hgen_sm`


# How to use it

In user_input.py you can provide the input values you want.
In config.yaml you can configure what should get plotted.

# Explanation of Abbreviations

- BP = Bending Point
- CP = Corner Point
- FP = Flange Point

- 0,1,2,... = ID of Tab

- A,B,C,D = Corner Points of user input rectangle

- L = Left Side of Flange
- R = Right Side of Flange

# Development Goals
- Part generation
	- [x] Generate solutions for 1 bend
	- [x] Generate solutions for 2 bend
	- [x] Extend part generation to multiple rectangles
	- [x] Filter solutions that are unsuitable
	- [x] Improve flange visuals
	- [x] Introduce collision filter
	- [ ] Improve angle filter
	- [ ] Introduce mounts
	- [ ] Introduce rule "Minimum distance mount from bend"
	- [ ] Generate solutions by separating surfaces
- Export
	- [x] Create JSON Export
	- [x] Connect to Onshape API (Creates Onshape Featurescript)
	- [ ] Check parts with TruTopsBoost
- README
	- [x] Extend installation guide
	- [x] Explain function more precisely

# Miscellaneous
[Image Gallery](assets/images/image_gallery.md)
