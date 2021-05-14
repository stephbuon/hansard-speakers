
from libc.math cimport floor
from libc.stdlib cimport malloc, free


cdef double _jaro_distance(const char* a,const char* b):
    cdef int len_a = len(a)
    cdef int len_b = len(b)
    
    cdef int max_dist = <int>(floor(max(len_a, len_b) / 2) - 1)
    
    cdef int match = 0
    
    cdef int *hash_a = <int *> malloc(len_a * sizeof(int))
    cdef int *hash_b = <int *> malloc(len_b * sizeof(int))
    
    if not hash_a or not hash_b:
        raise MemoryError()
    
    for i in range(len_a):
        hash_a[i] = 0
    for i in range(len_b):
        hash_b[i] = 0
    
    for i in range(len_a):
        for j in range(max(0, i - max_dist), min(len_b, i + max_dist + 1)):
            # If there is a match
            if a[i] == b[j] and hash_b[j] == 0:
                hash_a[i] = 1
                hash_b[j] = 1
                match += 1
                break
    
    # If there is no match
    if match == 0:
        free(hash_a)
        free(hash_b)
        return 0.0
    
    cdef int t = 0
    cdef int point = 0
    
    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len_a):
        if hash_a[i]:
            # Find the next matched character
            # in second
            while hash_b[point] == 0:
                point += 1
  
            if a[i] != b[point]:
                t += 1
            point += 1

    t = t//2
    
    free(hash_a)
    free(hash_b)
  
    # Return the Jaro Similarity
    return ((match / len_a) + (match / len_b) + ((match - t) / match)) / 3.0

    
cdef extern from "Python.h":
    const char* PyUnicode_AsUTF8(object unicode)
    
cpdef jaro_distance(object str_a,object str_b):
    cdef const char* a = PyUnicode_AsUTF8(str_a)
    cdef const char* b = PyUnicode_AsUTF8(str_b)
    return _jaro_distance(a, b)
