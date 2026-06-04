# Programming Exercises - June 05, 2026

## Exercise 1 : Bellman–Ford Algorithm

### Question : Write a program to compute shortest paths from a single source (allowing negative weights) and detect negative-weight cycles using the Bellman–Ford algorithm.

### Algorithm

1. Input number of vertices `V` and number of edges `E`.
2. Read the list of edges `(src, dest, weight)`.
3. Initialize distances `dist[]` to a large sentinel (e.g., `9999`), and set `dist[source] = 0`.
4. Relax all edges `V-1` times: for each edge `(u,v,w)` if `dist[u] + w < dist[v]` then `dist[v] = dist[u] + w`.
5. Check for negative-weight cycles by trying to relax once more; if any distance improves, report a negative cycle.
6. Otherwise, print the distances from the source to every vertex.

### Code

```cpp
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
```

### Output

Using the sample input provided below (source = 0):

```
Enter Number Of Vertices: Enter Number Of Edges: Enter Source Destination Weight For Each Edge :
Enter Source Vertex : 
Vertex  Distance From Source
0       0
1       -1
2       2
3       -2
4       1
```

Sample input used:

```
5
8
0 1 -1
0 2 4
1 2 3
1 3 2
1 4 2
3 2 5
3 1 1
4 3 -3
0
```
