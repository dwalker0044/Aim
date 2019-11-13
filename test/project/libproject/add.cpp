#if _WIN32 || _WIN64
    #define SHARED_EXPORT __declspec(dllexport)
#else
    #define SHARED_EXPORT __attribute__ ((visibility ("default")))
#endif

#include "add.h"

int add(int a, int b)
{
    return a+b;
}

int subtract(int a, int b)
{
    return a-b;
}