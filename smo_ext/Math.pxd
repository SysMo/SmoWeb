cimport CMath

cdef CMath.MemoryView1D[double]* createMemoryView1D(double [:] a)
cdef CMath.MemoryView2D[double]* createMemoryView2D(double [:, :] a)
cdef CMath.MemoryView3D[double]* createMemoryView3D(double [:, :, :] a)

