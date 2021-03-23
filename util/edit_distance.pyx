from libc.stdlib cimport abs



cdef bint _is_edit_distant_n(const char* incorrect,const char* correct, const int n):
    cdef int len_i = len(incorrect)
    cdef int len_c = len(correct)
    
    if abs(len_i - len_c) > n:
        return False
    
    cdef int j = 0
    cdef int i = 0
    cdef int count = 0
    
    while i < len_i and j < len_c:
        if incorrect[i] == correct[j]:
            i += 1
            j += 1
        else:
            # characters don't match
            if count >= n:
                # Too many edits.
                return False

            if len_i == len_c:
                # substitution
                i += 1
                j += 1
            else:
                # Increment if one string is longer than the other
                i += len_i > len_c  # (Insertion)
                j += len_c > len_i  # (Deletion)

            count += 1

    # Excess trailing character(s)
    if i < len_i or j < len_c:
        count += abs(len_i - len_c)

    return count <= n


cdef extern from "Python.h":
    const char* PyUnicode_AsUTF8(object unicode)

cpdef within_distance_one(object incorrect,object correct):
    cdef const char* a = PyUnicode_AsUTF8(incorrect)
    cdef const char* b = PyUnicode_AsUTF8(correct)
    return _is_edit_distant_n(a, b, 1)

cpdef within_distance_four(object incorrect,object correct):
    cdef const char* a = PyUnicode_AsUTF8(incorrect)
    cdef const char* b = PyUnicode_AsUTF8(correct)
    return _is_edit_distant_n(a, b, 4)
