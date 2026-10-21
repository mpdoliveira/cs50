#include <stdio.h>
#include <cs50.h>
#include <string.h>

bool valid_triangle(float x, float y, float z);

int main(void)
{
    float sides[3];
    for (int i = 0; i < 3; i++)
    {
        sides[i] = get_float("Side of the triangle: ");
    }
    bool result = valid_triangle(sides[0], sides[1], sides[2]);
    if (result == true)
    {
        printf("True\n");
    }
    else
    {
        printf("False\n");
    }
}

bool valid_triangle(float x, float y, float z)
{
    if (x == 0 || y == 0 || z == 0)
    {
        return false;
    }
    if ((x + y <= z) || (x + z <= y) || (y + z <= x))
    {
        return false;
    }
    return true;
}