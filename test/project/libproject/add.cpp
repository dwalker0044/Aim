#define SHARED_EXPORT __declspec(dllexport)
#include "add.h"

int add(int a, int b)
{
    return a+b;
}

int subtract(int a, int b)
{
    return a-b;
}