findneighsides is a simple python script that solves the "find neighbor" and "find neighboring sides" problems in a given triangulation.

- "Find neighbor" problem: given a list of 3-tuples of vertex indices of cells in a tiling, what are the neighbors of each cell? I.e. for each element, wich elements share a side with it?
- "Find neighboring sides" problem: given a list of 3-tuples of vertex indices of cells whose sides are numbered, which side of each cell is shared with which side of its neighbors? I.e. for each element and each of its sides, if a neighboring element shares that side, what is that neighbor's side number for the side that's shared?

The script is really CPU-intensive since it iterates over each cell sequentially (without multithreading), but it should be able to manage big meshes without more issues than a longer runtime. For vectorized approaches (with RAM limitations), try findneighsides2 or findneighsideswave.

It appears to me the algorithm is super parallelizable since it's completely asynchronous in theory, however I'm not well versed enough in multithreading to implement this. Any advice is very welcome.
