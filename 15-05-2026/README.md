# Programming Exercises - May 15, 2026

## Exercise 1 : Kruskal's Algorithm

## Question : Write A Program To Find The Minimum Spanning Tree Using Kruskal's Algorithm

### Algorithm

1. Input the number of vertices n
2. Input the adjacency matrix cost[n][n]
3. Replace 0 with INF for non-diagonal elements to indicate no edge
4. Convert the upper triangle of adjacency matrix into edge list
5. Sort all edges in ascending order of weight
6. Initialize each vertex as a separate set
7. For each edge (u, v) in sorted order:
    - If u and v belong to different sets:
        - Include edge in MST
        - Add edge weight to minimumCost
        - Merge the two sets
8. Stop when MST has n - 1 edges
9. If MST has fewer than n - 1 edges, report that MST cannot be formed
10. Otherwise, print the selected edges and minimumCost

### Code

```c
#include <stdio.h>

#define INF 999999

// Edges
struct Edge
{
    int u, v, weight;
};

void kruskalAlgorithm(int vertices, int cost[vertices][vertices])
{

    int i, j;

    struct Edge edges[vertices * vertices];
    int edgeCount = 0;

    // Convert Adjacency Matrix To Edge List
    for (i = 0; i < vertices; i++)
    {

        for (j = i + 1; j < vertices; j++)
        {

            if (cost[i][j] != INF)
            {

                edges[edgeCount].u = i;
                edges[edgeCount].v = j;
                edges[edgeCount].weight = cost[i][j];

                edgeCount++;
            }
        }
    }

    // Sort Edges By Weight ( Bubble Sort )
    for (i = 0; i < edgeCount - 1; i++)
    {

        for (j = 0; j < edgeCount - i - 1; j++)
        {

            if (edges[j].weight > edges[j + 1].weight)
            {

                struct Edge temp = edges[j];
                edges[j] = edges[j + 1];
                edges[j + 1] = temp;
            }
        }
    }

    // Array To Store Set Number
    int set[vertices];

    // Initially Every Vertex Belongs To Different Set
    for (i = 0; i < vertices; i++)
    {
        set[i] = i;
    }

    int minimumCost = 0;
    int mstEdges = 0;

    printf("\nEdges In MST :\n");

    // Process Sorted Edges
    for (i = 0; i < edgeCount && mstEdges < vertices - 1; i++)
    {

        int u = edges[i].u;
        int v = edges[i].v;
        int weight = edges[i].weight;

        // If Vertices Belong To Different Sets
        if (set[u] != set[v])
        {

            printf("%d --> %d = %d\n", u, v, weight);

            minimumCost += weight;
            mstEdges++;

            // Merge Sets
            int oldSet = set[v];
            int newSet = set[u];

            for (j = 0; j < vertices; j++)
            {

                if (set[j] == oldSet)
                {
                    set[j] = newSet;
                }
            }
        }
    }

    // Check If MST Is Possible
    if (mstEdges != vertices - 1)
    {
        printf("\nMST Cannot Be Formed\n");
    }
    else
    {
        printf("\nMinimum Cost = %d\n", minimumCost);
    }
}

int main()
{

    int i, j, vertices;

    printf("Enter The Number Of Vertices : ");
    scanf("%d", &vertices);

    int cost[vertices][vertices];

    printf("Enter The Cost Of Adjacency Matrix :\n");

    for (i = 0; i < vertices; i++)
    {

        for (j = 0; j < vertices; j++)
        {

            scanf("%d", &cost[i][j]);

            // Replace O With Infinity ( 999 )
            if (i != j && cost[i][j] == 0)
            {
                cost[i][j] = INF;
            }
        }
    }

    kruskalAlgorithm(vertices, cost);

    return 0;
}
```

### Output

```bash
Enter The Number Of Vertices : 4
Enter The Cost Of Adjacency Matrix :
0 10 6 5
10 0 0 15
6 0 0 4
5 15 4 0

Edges In MST :
2 --> 3 = 4
0 --> 3 = 5
0 --> 1 = 10

Minimum Cost = 19
```

## Exercise 2 : Matrix Chain Multiplication

## Question : Write a program to find the minimum number of scalar multiplications needed to multiply a chain of matrices using dynamic programming. Also compute the number of ways to parenthesize the chain

### Algorithm (Dynamic Programming)

1. Let `numberOfMatrices = n` and `Matrices[]` be the dimension array of length `n+1`.
2. Initialize `cost[i][i] = 0` for all `i` (single matrix multiplication costs zero).
3. For chain lengths `L` from `2` to `n`:
   - For each starting index `i` from `0` to `n - L`:
     - Let `j = i + L - 1`.
     - Initialize `cost[i][j]` to a large value (infinity).
     - For each split point `k` from `i` to `j-1`:
       - Compute `q = cost[i][k] + cost[k+1][j] + Matrices[i] * Matrices[k+1] * Matrices[j+1]`.
       - If `q < cost[i][j]`, update `cost[i][j] = q` and record `splits[i][j] = k`.
4. The minimum cost is `cost[0][n-1]`.

### Code

```cpp
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
```

### Output

``` bash
The Dimensions Of The Matrices Are :
Matrix A1: 10 X 20
Matrix A2: 20 X 30
Matrix A3: 30 X 40

The Number Of Ways To Parenthesize The Matrices Is : 2
The Minimum Number Of Scalar Multiplications Required Is : 18000
```
