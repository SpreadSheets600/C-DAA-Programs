#include <stdio.h>

struct Edge
{
    int src, dest, weight;
};

int main()
{
    int V, E;

    printf("Enter Number Of Vertices: ");
    scanf("%d", &V);

    printf("Enter Number Of Edges: ");
    scanf("%d", &E);

    struct Edge edges[E];

    printf("Enter Source Destination Weight For Each Edge :\n");
    for (int i = 0; i < E; i++)
    {
        scanf("%d %d %d",
              &edges[i].src,
              &edges[i].dest,
              &edges[i].weight);
    }

    int source;
    printf("Enter Source Vertex : ");
    scanf("%d", &source);

    int dist[V];

    for (int i = 0; i < V; i++)
        dist[i] = 9999;

    dist[source] = 0;

    // Relax Edges V-1 Times
    for (int i = 1; i < V; i++)
    {
        for (int j = 0; j < E; j++)
        {
            int u = edges[j].src;
            int v = edges[j].dest;
            int w = edges[j].weight;

            if (dist[u] != 9999 && dist[u] + w < dist[v])
            {
                dist[v] = dist[u] + w;
            }
        }
    }

    // Check For Negative Weight Cycles
    for (int j = 0; j < E; j++)
    {
        int u = edges[j].src;
        int v = edges[j].dest;
        int w = edges[j].weight;

        if (dist[u] != 9999 && dist[u] + w < dist[v])
        {
            printf("Negative Weight Cycle Detected!\n");
            return 0;
        }
    }

    printf("\nVertex\tDistance From Source\n");
    for (int i = 0; i < V; i++)
    {
        printf("%d\t%d\n", i, dist[i]);
    }

    return 0;
}
