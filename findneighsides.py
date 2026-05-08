import numpy as np
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from timeit import timeit

import itertools

import os

ncpus = os.cpu_count()

# Number of rows to dispatch to each task
chunk_size = 4




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
     

This implementation relies on python's multithreading, GIL-free capabilities, but the idea should be the same for other multiprocessing libraries. This algorithm can
be easily extended to arbitrary (even higher-dimensional) non-ramified tilings by translating "sides" into "faces" and all their concerning instructions.

It also has the option to load a text file containing the indices of cells to remove from the tiling, but I haven't tested what happens if one removes enough cells
to leave nodes isolated. I suspect that would be fine, but the resulting answers would assume the existence of said unused, isolated nodes.

-Juan Andrés Fuenzalida A. Contact: juan[dot]fuenzalidaa[at]sansano[dot]usm[dot]cl
"""

elements=np.loadtxt("test.txt",dtype=int)#load nodes faces array
#elements=elements-1 #turn into 0-index if 1-indexed

bad_cells=None
#bad_cells=np.loadtxt("bad_cells.txt",dtype=int) #Bad cells to further remove

if bad_cells is not None:
    elements=np.delete(elements,bad_cells,0)

ElemNeighs=np.zeros_like(elements)
ElemNeighSides=np.zeros_like(elements)

def thread_worker(j_verts,lelements):
    for (j,element) in j_verts:
        neighs = np.array((0,0,0))
        neighsides = np.array((0,0,0))
        for (nside,verts) in enumerate(((0,1),(1,2),(2,0))):
            side = np.take(element,verts)
            elems_with_nodes=np.vstack(np.where(np.isin(lelements,side))).T
            r,c=np.unique(elems_with_nodes[:,0],return_counts=True)
            if np.count_nonzero(c-1)>1:
                neighcell=np.setdiff1d(r[c>1],np.array(j))
                neighs[nside]=neighcell[0]
                x=np.sum(elems_with_nodes[elems_with_nodes[:,0]==neighcell][:,1])
                neighsides[nside] = (int(np.ceil(-(x-1)*(x-3.5))))
            else:
                neighs[nside]=-1
                neighsides[nside]=-1

        ElemNeighs[j]=neighs
        ElemNeighSides[j]=neighsides
        completed=np.count_nonzero(ElemNeighs)/(ElemNeighs.size)*100
        print(f'{completed:.2f}% Completed \r')

def run_thread_pool(num_workers):
    with ThreadPoolExecutor(max_workers=num_workers) as tpe:
        chunks = itertools.batched(enumerate(elements), chunk_size,strict=False)
        try:
            futurez = [tpe.submit(thread_worker,arg,elements.copy()) for arg in chunks]
            # block until all work finishes
            concurrent.futures.wait(futurez)
        finally:
            # check for exceptions in worker threads
            [f.result() for f in futurez]

run_thread_pool(ncpus)

np.savetxt('ElemNeighsFound.txt',ElemNeighs,fmt="%1d")
np.savetxt('ElemNeighSidesFound.txt',ElemNeighSides,fmt="%1d")
np.savetxt('ElemNodesNew.txt',elements,fmt='%1d')

pass

