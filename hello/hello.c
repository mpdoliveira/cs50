#include <stdio.h>
#include <cs50.h>

int main(void)
{
    //asks the users name
    string name = get_string("What's your name? ");
    //says hello to the user
    printf("hello, %s\n", name);
}