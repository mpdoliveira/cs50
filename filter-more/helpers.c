#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{

    // puts eack pixel in the greyscale
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            if (image[i][j].rgbtRed != image[i][j].rgbtGreen || image[i][j].rgbtGreen != image[i][j].rgbtBlue)
            {
                float avgColor = ((float)image[i][j].rgbtRed + image[i][j].rgbtGreen + image[i][j].rgbtBlue) / 3;

                // make RGB parameters the same asigning them their average
                image[i][j].rgbtRed = round(avgColor);
                image[i][j].rgbtGreen = round(avgColor);
                image[i][j].rgbtBlue = round(avgColor);
            }
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];

    // makes a temporary copy of the image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j].rgbtRed = image[i][j].rgbtRed;
            copy[i][j].rgbtGreen = image[i][j].rgbtGreen;
            copy[i][j].rgbtBlue = image[i][j].rgbtBlue;
        }
    }

    // flips the image horizontaly using copy as reference
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed = copy[i][width - j - 1].rgbtRed;
            image[i][j].rgbtGreen = copy[i][width - j - 1].rgbtGreen;
            image[i][j].rgbtBlue = copy[i][width - j - 1].rgbtBlue;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];

    // make a copy of image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j].rgbtRed = image[i][j].rgbtRed;
            copy[i][j].rgbtGreen = image[i][j].rgbtGreen;
            copy[i][j].rgbtBlue = image[i][j].rgbtBlue;
        }
    }

    // blurs image using copy as reference
    // i and j go through every pixel of the image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sumRed = 0;
            int sumGreen = 0;
            int sumBlue = 0;
            int counter = 0;

            // k and j go through the 8 pixels surounding and the pixel itself
            for (int k = i - 1; k < i + 2; k++)
            {
                for (int l = j - 1; l < j + 2; l++)
                {
                    if (k > -1 && k < height && l > -1 && l < width) //discarts "invalid pixels" outside of the picture
                    {
                        // adds RGB values of the 9 pixels
                        sumRed += copy[k][l].rgbtRed;
                        sumGreen += copy[k][l].rgbtGreen;
                        sumBlue += copy[k][l].rgbtBlue;

                        // counts valid pixels
                        counter++;
                    }
                }
            }

            // asign the average of each RGB values
            image[i][j].rgbtRed = round((float)sumRed / counter);
            image[i][j].rgbtGreen = round((float)sumGreen / counter);
            image[i][j].rgbtBlue = round((float)sumBlue / counter);
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];

    // make a copy of image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j].rgbtRed = image[i][j].rgbtRed;
            copy[i][j].rgbtGreen = image[i][j].rgbtGreen;
            copy[i][j].rgbtBlue = image[i][j].rgbtBlue;
        }
    }

    // Gx and Gy
    int gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    // i and j go through every pixel of the image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int gxR = 0;
            int gxG = 0;
            int gxB = 0;
            int gyR = 0;
            int gyG = 0;
            int gyB = 0;

            // k and j go through the 8 pixels surounding and the pixel itself
            for (int k = i - 1, m = 0; k < i + 2; k++, m++)
            {
                for (int l = j - 1, n = 0; l < j + 2; l++, n++)
                {
                    if (k > -1 && k < height && l > -1 && l < width)
                    {
                        // Gx for three colors
                        gxR += gx[m][n] * copy[k][l].rgbtRed;
                        gxG += gx[m][n] * copy[k][l].rgbtGreen;
                        gxB += gx[m][n] * copy[k][l].rgbtBlue;

                        //Gy for three colors
                        gyR += gy[m][n] * copy[k][l].rgbtRed;
                        gyG += gy[m][n] * copy[k][l].rgbtGreen;
                        gyB += gy[m][n] * copy[k][l].rgbtBlue;
                    }
                }
            }

            // calculates final G = Gx^2 + Gy^2 and rounds it properly
            int gRTotal = round(sqrt((float)(gxR * gxR) + (gyR * gyR)));
            int gGTotal = round(sqrt((float)(gxG * gxG) + (gyG * gyG)));
            int gBTotal = round(sqrt((float)(gxB * gxB) + (gyB * gyB)));

            // red values
            if (gRTotal > 255) // G bigger than 255
            {
                image[i][j].rgbtRed = 255;
            }
            else if (gRTotal < 0) // G smaller than 255
            {
                image[i][j].rgbtRed = 0;
            }
            else
            {
                image[i][j].rgbtRed = gRTotal;
            }

            // blue values
            if (gGTotal > 255) // G bigger than 255
            {
                image[i][j].rgbtGreen = 255;
            }
            else if (gGTotal < 0) // G smaller than 255
            {
                image[i][j].rgbtGreen = 0;
            }
            else
            {
                image[i][j].rgbtGreen = gGTotal;
            }

            // green values
            if (gBTotal > 255) // G bigger than 255
            {
                image[i][j].rgbtBlue = 255;
            }
            else if (gBTotal < 0) // G smaller than 255
            {
                image[i][j].rgbtBlue = 0;
            }
            else
            {
                image[i][j].rgbtBlue = gBTotal;
            }
        }
    }
    return;
}