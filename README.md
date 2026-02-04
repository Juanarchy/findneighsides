findneighsides2 is a simple python script that solves the "find neighbor" and "find neighboring sides" problems in a given triangulation.

- "Find neighbor" problem: given a list of 3-tuples of vertices of cells in a tiling, what are the neighbors of each cell?
- "Find neighboring sides" problem: given a list of 3-tuples of vertices of cells in a tiling whose sides are numbered, which side of each cell is shared with which side of its neighbors?

The script is really CPU-intensive since it iterates over each cell sequentially (without multithreading), but it should be able to manage big meshes without more issues than a longer runtime. For vectorized approaches (with RAM limitations), try findneighsides2 or findneighsideswave.
