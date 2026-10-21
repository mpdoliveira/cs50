#include <cs50.h>
#include <stdio.h>

//functions
int single_digit(long number, int power);
int number_size(long number);
void invalid(void);

int main(void)
{
    const long credit = get_long("Number: "); //asks the user the credit number
    long number = credit;
    int power, correct = 0, add = 0;


    const int SIZE = number_size(number); //gets for the size of the number

    //***STARTING CHECKSUM***

    for (int i = 2; i <= SIZE; i += 2) //gets every other number from the second digit to the last
    {
        power = i;
        number = credit;
        int digit = single_digit(number, power);
        if (digit > 4) //Corrects the double digit numbers
        {
            for (int j = 1; j <= 2; j++)
            {
                number = 2 * digit; //doubles the number to make the correction
                power = j;
                correct += single_digit(number, power); //adds each digit of the double-digit numbers
            }
            add += correct; //adds the number after correction
            correct = 0; //restarts the correct variable
        }
        else //if there's no need for correction, adds the digits
        {
            add += 2 * digit;
        }
    }
    for (int i = 1; i <= SIZE; i += 2) //gets the rest of the numbers
    {
        number = credit; //restanting number and power to avoid bugs
        power = i;
        int digit = single_digit(number, power);
        add += digit; //add the numbers to the total
    }

    //***CHECKING RESULTS***
    if (add % 10 == 0 && SIZE >= 13 && SIZE <= 16) //roughly filters the card numbers
    {
        power = SIZE;
        int digit = single_digit(number, power); //gets the first number from left to right
        power = SIZE - 1;
        int digit_2 = single_digit(number, power); //gets the second number from left to right

        if (SiZE == 15 && digit == 3) //checks if it is an Amex card number or not
        {
            if (digit_2 == 4 || digit_2 == 7)
            {
                printf("AMEX\n");
            }
            else
            {
                invalid(); //invalidates the number
            }
        }

        if (SIZE == 16 && digit == 5) //checks if it is an Mastercard card number or not
        {
            if (digit_2 == 1 || digit_2 == 2 || digit_2 == 3 || digit_2 == 4 || digit_2 == 5)
            {
                printf("MASTERCARD\n");
            }
            else
            {
                invalid(); //invalidates the number
            }
        }

        if ((size == 13 || size == 16) && digit == 4) //checks if it is an Visa card number
        {
            printf("VISA\n");
        }
    }
    else
    {
        invalid(); //invalidates the number
    }
}









//***PRINTS INVALID***
void invalid(void)
{
    printf("INVALID\n");
}


//***GETS THE SIZE OF THE NUMBER***
int number_size(long number)
{
    int i;
    for (i = 0; number > 0 ; i++) //initiate counting
    {
        number /= 10; //decreases the number
    }
    return i;
}


//***GETS ONE SPECIFIC DIGIT OF THE WHOLE NUMBER***
int single_digit(long number, int power)
{
    long digit, dec;
    for (dec = 1; power > 0; power--) //gets the power of ten
    {
        dec *= 10;
    }
    digit = number % dec;
    dec /= 10;
    digit -= (number % dec); //removes the rest of the number
    digit /= dec; //removes the zeros
    return digit;
}