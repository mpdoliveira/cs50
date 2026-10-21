#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    //Ensures proper usage
    if (argc != 2)
    {
        printf("Usage: ./recover infile\n");
        return 1; //error
    }

    //Ppens input file
    FILE *in_file = fopen(argv[1], "r");
    //Cheks if input file isnt empty
    if (in_file == NULL)
    {
        return 2; //error
    }

    //Sets output file pointer to NULL
    FILE *out_file = NULL;

    //Holds output filename
    char filename[8] = {0};

    //Buffer for one chunk of 512 bytes
    BYTE block[512];

    //Counter for number jpeg files
    int jpeg_count = 0;

    //Repeats while fread has not riched end of input file
    while (fread(block, sizeof(BYTE) * 512, 1, in_file) == 1)
    {
        //Checks for jpeg headers
        if (block[0] == 0xff && block[1] == 0xd8 && block[2] == 0xff && (block[3] & 0xf0) == 0xe0)
        {
            //Closes previous opened output files
            if (out_file != NULL)
            {
                fclose(out_file);
            }

            //Sets new name to filename
            sprintf(filename, "%03i.jpg", jpeg_count);
            jpeg_count++;

            //Opens new output file
            out_file = fopen(filename, "w");
        }

        //Writes on latest output file
        if (out_file != NULL)
        {
            fwrite(block, sizeof(BYTE) * 512, 1, out_file);
        }
    }

    //Closes last output file
    if (out_file != NULL)
    {
        fclose(out_file);
    }

    //Closes input file
    fclose(in_file);

    return 0;



}