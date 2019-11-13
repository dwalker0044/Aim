#ifndef ADD_H
#define ADD_H

#ifdef SHARED_EXPORT
#else
    #if _WIN32 || _WIN64
        #define SHARED_EXPORT __declspec(dllimport)
    #else
        #define SHARED_EXPORT
    #endif
#endif

SHARED_EXPORT
int add(int, int);

SHARED_EXPORT
int subtract(int a, int b);

#endif