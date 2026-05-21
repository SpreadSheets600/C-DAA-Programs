#include <stdio.h>

#define INF 999999

int factorial(int n)
{
    if (n == 0 || n == 1)
    {
        return 1;
    }
    else
    {
        return n * factorial(n - 1);
    }
}

int MatrixChainParenthesization(int numberOfMatrices)
{
    // Formula : P(n) = 1/n * (2n - 2)! / (n - 1)! * ((2n - 2) - (n - 1))!
    return (factorial(2 * numberOfMatrices - 2) / (factorial(numberOfMatrices - 1) * factorial(2 * numberOfMatrices - 2 - (numberOfMatrices - 1)))) / numberOfMatrices;
}

int MatrixChainMultiplication(int numberOfMatrices, int Matrices[])
{
    int cost[numberOfMatrices][numberOfMatrices];
    int splits[numberOfMatrices][numberOfMatrices];

    for (int i = 0; i < numberOfMatrices; i++)
    {
        cost[i][i] = 0; // Cost Of Multiplying One Matrix Is Zero
    }

    for (int L = 2; L <= numberOfMatrices; L++) // L Is The Chain Length
    {
        for (int i = 0; i < numberOfMatrices - L + 1; i++)
        {
            int j = i + L - 1;
            cost[i][j] = INF; // Initialize Cost To Infinity

            for (int k = i; k < j; k++)
            {
                // Cost Of Multiplying The Two Subchains And The Resulting Matrix
                int q = cost[i][k] + cost[k + 1][j] + Matrices[i] * Matrices[k + 1] * Matrices[j + 1];

                if (q < cost[i][j])
                {
                    cost[i][j] = q;   // Update Cost If A Cheaper Way Is Found
                    splits[i][j] = k; // Update Split Point
                }
            }
        }
    }
    return cost[0][numberOfMatrices - 1];
}

int main()
{
    int numberOfMatrices;

    printf("Enter The Number Of Matrices : ");
    if (scanf("%d", &numberOfMatrices) != 1)
        return 1;

    int matrices[numberOfMatrices + 1];

    printf("Enter The Dimensions Of The Matrices (%d elements) : ", numberOfMatrices + 1);
    for (int i = 0; i < numberOfMatrices + 1; i++)
    {
        if (scanf("%d", &matrices[i]) != 1)
            return 1;
    }

    printf("\nThe Dimensions Of The Matrices Are : \n");
    for (int i = 0; i < numberOfMatrices; i++)
    {
        printf("Matrix A%d: %d X %d\n", i + 1, matrices[i], matrices[i + 1]);
    }
    printf("\n");

    printf("The Number Of Ways To Parenthesize The Matrices Is : %d\n", MatrixChainParenthesization(numberOfMatrices));

    int minCost = MatrixChainMultiplication(numberOfMatrices, matrices);
    printf("The Minimum Number Of Scalar Multiplications Required Is : %d\n", minCost);

    return 0;
}