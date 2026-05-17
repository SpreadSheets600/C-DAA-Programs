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
