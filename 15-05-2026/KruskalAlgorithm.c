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
