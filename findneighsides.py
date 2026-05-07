import numpy as np

"""
This script loads a shape (nElems,3) array from a text file whose i-th row contains the index of the (possibly 1-indexed) nodes at each vertex of the i-th triangle 
of a non-ramified triangulation, and saves 3 text files containing each:
    - A shape (nElems,3) array whose i-th row contains, at position j, the index of the cell that neighbors cell i from side j. (ElemNeighsFound.txt)
    - A shape (nElems,3) array whose i-th row contains, at position j, the limiting side of the cell that neighbors cell i from side j. (ElemNeighSidesFound.txt)
    - A shape (nElems,3) array whose i-th row contains the index of the (now 0-indexed) nodes at each vertex of the i-th triangle. (ElemNodesNew.txt)
                 X
                / \ 
               /   \ 
              /     \ 
     X-------X-------X 
      \     / \  1  / \ 
       \   /1n0\2m0/   \      In this example, cell n has cell m as a neighbor from its side 0, while cell m has cell n as a neighbor from
        \ /  2  \ /     \     its side 2. Therefore: 
         X-------X-------X 
        / \     / \               - ElemNeighs[n,0] == m
       /   \   /   \              - ElemNeighs[m,2] == n
      /     \ /     \             - ElemNeighSides[n,0] == 2
     X-------V-------X            - ElemNeighSides[m,2] == 0
     

Its implemented algorithm iterates over each cell, comparing the three sides of the cell to the three sides of each other cell and positions neighbors and 
sides accordingly. This "indifferent" approach means that it can efficiently be parallelized through multithread/core/device python APIs. This algorithm can
be easily extended to arbitrary (even higher-dimensional) non-ramified tilings by translating "sides" into "faces" and all their concerning instructions.

It also has the option to load a text file containing the indices of cells to remove from the tiling, but I haven't tested what happens if one removes enough cells
to leave nodes isolated. I suspect that would be fine, but the resulting answers would assume the existence of said unused, isolated nodes.

-Juan Andrés Fuenzalida A. Contact: juan[dot]fuenzalidaa[at]sansano[dot]usm[dot]cl
"""

elements=np.loadtxt("ElemNodesMatlab.txt",dtype=int)#load nodes faces array
elements=elements-1 #turn into 0-index if 1-indexed
bad_cells=np.loadtxt("celdasmals.txt")

#bad_cells=np.loadtxt("bad_cells.txt",dtype=int) #Bad cells to further remove

if bad_cells is not None:
    elements=np.delete(elements,bad_cells,0)


ElemNeighs=[]
ElemNeighSides=[]
i=0
for element in elements:
    neighs=[]
    neighsides=[]
    for verts in [(0,1),(1,2),(2,0)]:
        side=np.take(element,verts)
        elems_with_nodes=np.vstack(np.where(np.isin(elements,side))).T
        r,c=np.unique(elems_with_nodes[:,0],return_counts=True)
        if np.count_nonzero(c-1)>1:
            neighcell=np.setdiff1d(r[c>1],np.array(i))
            neighs.append(neighcell[0])
            x=np.sum(elems_with_nodes[elems_with_nodes[:,0]==neighcell][:,1])
            neighsides.append(int(np.ceil(-(x-1)*(x-3.5))))
        else:
            neighs.append(-1)
            neighsides.append(-1)
    ElemNeighs.append(neighs)
    ElemNeighSides.append(neighsides)
    i+=1

np.savetxt('ElemNeighsFound.txt',ElemNeighs,fmt="%1d")
np.savetxt('ElemNeighSidesFound.txt',ElemNeighSides,fmt="%1d")
np.savetxt('ElemNodesNew.txt',elements,fmt='%1d')

pass

