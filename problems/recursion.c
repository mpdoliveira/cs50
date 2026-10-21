#include <stdio.h>
#include <cs50.h>

int collatz(int n);

int main (void)
{
    int number = get_int("What's the number? ");
    int answer = collatz(number);
    printf("%i\n", answer);
}

int collatz(int n)
{
    // base case
    if (n == 1)
    {
        printf("%i\n", n);
        return true;
    }
    // even numbers
    else if ((n % 2) == 0)
    {
        printf("%i -> ", n);
        return collatz(n/2);
    }
    // odd numbers
    else
    {
        printf("%i -> ", n);
        return collatz(3 * n + 1);
    }
}