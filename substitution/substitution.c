#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int validates_key(string s, int c);
string uniformalize(string s);
string crypter(string text, string cipher);

int main(int argc, string argv[])
{
    if (argv[1] == 0) //Checks if KEY exists
    {
        printf("Usage: ./substitution KEY\n");
        return 1;
    }

    string cipher = uniformalize(argv[1]); // Standardize cipher
    int n = validates_key(cipher, argc); // Checks if KEY is valid
    if (n != 0) // Returns the status quo
    {
        return n;
    }

    string text = get_string("plaintext:  "); // Prompts the user for the uncipherd text
    text = crypter(text, cipher); // Calls the crypter and assignes the crypted message to text
    printf("ciphertext: %s\n", text); // Prints the result
}




// Makes all letters upper case
string uniformalize(string s)
{
    for (int i = 0, n = strlen(s); i < n; i++)
    {
        s[i] = toupper(s[i]);
    }
    return s; // Returns the upper case cipher string
}

//Cheks if the KEY is valid
int validates_key(string s, int argc)
{
    if (argc != 2)
    {
        printf("Usage: ./substitution KEY\n");
        return 1;
    }
    // If KEY has the wrong number of characters
    if (strlen(s) != 26)
    {
        printf("Key must contain 26 characters.\n");
        return 1;
    }
    // If KEY has characters other than letters
    for (int i = 0; i < 26; i++)
    {
        if (s[i] < 65 || s[i] > 90)
        {
            printf("Key must only contain alphabetic characters. \n");
            return 1;
        }
    }
    // If KEY has repetitive characters
    for (int i = 0; i < 26; i++)
    {
        for (int j = i + 1; j < 26; j++)
        {
            if (s[i] == s[j])
            {
                return 1;
            }
        }
    }


    // Cipher approved
    return 0;
}

string crypter(string text, string cipher)
{
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        // char uppercase
        if (text[i] >= 65 && text[i] <= 90)
        {
            text[i] = cipher[text[i] - 65];
        }
        // char lowercase
        else if (text[i] >= 97 && text[i] <= 122)
        {
            text[i] = cipher[text[i] - 97];
            text[i] = tolower(text[i]);
        }
    }
    return text;
}