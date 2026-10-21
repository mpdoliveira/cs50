#include <cs50.h>
#include <stdio.h>

void blank(void);
void brick(void);

int main(void)
{
    int height, floor;
    const int CENTER = 2;

    //inputs user for a hight between 0 and 8
    do
    {
        height = get_int("Height: ");
        floor = height - 1;
    }
    while (height < 1 || height > 8);


    //prints rows
    for (int i = 0; i < height; i++)
    {
        int gap = 0;
        //prints rising stairs
        for (int j = 0; j < height; j++)
        {
            if (gap < floor)
            {
                blank();
            }
            else
            {
                brick();
            }
            gap++;
        }
        //prints blanks
        for (int j = 0; j < CENTER; j++)
        {
            blank();
        }
        gap = 0;
        //prints descending stairs
        for (int j = 0; j < height; j++)
        {
            if (gap < height - floor)
            {
                brick();
            }
            gap++;
        }
        floor--;
        printf("\n");
    }
}

// prints a blank space
void blank(void)
{
    printf(" ");
}

// prints a "brick"
void brick(void)
{
    printf("#");
}