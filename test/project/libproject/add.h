#ifndef ADD_H
#define ADD_H

#ifdef SHARED_EXPORT
#else
#define SHARED_EXPORT __declspec(dllimport)
#endif

SHARED_EXPORT
int add(int, int);

SHARED_EXPORT
int subtract(int a, int b);

#endif