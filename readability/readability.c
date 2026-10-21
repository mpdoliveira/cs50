#include <cs50.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <math.h>

// FUNCTIONS
void text_counter(string);
void prints_grade(int grade);
int grade_calculator(void);

// GLOBAL VARIABLES
int letters = 0, words = 1, sentences = 0;

int main(void)
{
    string text = get_string("Text: ");
    text_counter(text);
    prints_grade(grade_calculator());
}

void text_counter(string text)
{
    for (int i = 0, lenth = strlen(text); i < lenth; i++) //checks the i-valued char for as long as i is smaller than the string's lenth
    {
        // counts alphabetical characters
        if (isalpha(text[i]) != 0)
        {
            letters++;
        }
        // counts spaces
        if (text[i] == 32)
        {
            words++; // words = spaces + 1
        }
        // counts sentences using "?", "!" or "."
        if (text[i] == 33 || text[i] == 46 || text[i] == 63)
        {
            sentences++;
        }
    }
}

void prints_grade(int grade)
{
    if (grade < 1) // grade lower than 1 (min)
    {
        printf("Before Grade 1\n");
    }
    else if (grade > 16) // grades higher than 16 (max)
    {
        printf("Grade 16+\n");
    }
    else // grades from 1 to 16
    {
        printf("Grade %i\n", grade);
    }
}

int grade_calculator(void)
{
    float avg_letters = (float)letters / words * 100; // average letters per 100 words
    float avg_sentences = (float)sentences / words * 100; // average sentences per 100 words
    float grade = (0.0588 * avg_letters) - (0.296 * avg_sentences) - 15.8; //calculates the Coleman-Liau index and assigns it to grade
    grade = (int) round(grade); // rounds grade to the closest integer
    return grade;
}