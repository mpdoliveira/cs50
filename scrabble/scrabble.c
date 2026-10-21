#include <ctype.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Points assigned to each letter of the alphabet
int POINTS[] = {1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};

int compute_score(char *word);
void prints_result(int difference);

int main(void)
{
    // Get input words from both players
    char *word1 = get_string("Player 1: ");
    char *word2 = get_string("Player 2: ");

    // Score both words
    int score1 = compute_score(word1);
    int score2 = compute_score(word2);

    // Prints the result
    prints_result(score1 - score2);
}

int compute_score(char *word)
{
    int total = 0;

    // Checks points for each letter
    for (int i = 0, word_length = strlen(word); i < word_length; i++)
    {
        word[i] = tolower(word[i]);
        if (word[i] >= 97 && word[i] <= 122)
        {
            //adds points to total
            total += POINTS[word[i] - 97];
        }
    }
    return total;
}

void prints_result(int difference)
{
    //checks who won and prints the winner
    if (difference > 0)
    {
        printf("Player 1 wins\n");
    }
    else if (difference < 0)
    {
        printf("Player 2 wins\n");
    }
    else //in case of tie
    {
        printf("Tie!\n");
    }
}
