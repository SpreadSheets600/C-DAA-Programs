# Programming Exercises - May 29, 2026

## Exercise : Floyd–Warshall Algorithm

### Question : Write a program to compute shortest paths between all pairs of vertices using the Floyd–Warshall algorithm

### Algorithm

1. Input the number of vertices `n` and the adjacency matrix `dist[n][n]` where a large sentinel (e.g., `999`) represents infinity/no direct edge.
2. For each intermediate vertex `k` from `0` to `n-1`:
   - For each pair of vertices `(i, j)` update `dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])`.
3. After processing all intermediate vertices, `dist[i][j]` holds the length of the shortest path from `i` to `j` (or the sentinel if no path exists).
4. Print the resulting shortest-distance matrix, displaying `INF` for sentinel values.

### Code

```cpp
#include <stdio.h>

int main()
{
    int n;

    printf("Enter Number Of Vertices : ");
    scanf("%d", &n);

    int dist[n][n];

    printf("Enter Adjacency Matrix :\n");
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            scanf("%d", &dist[i][j]);
        }
    }

    for (int k = 0; k < n; k++)
    {
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < n; j++)
            {
                if (dist[i][k] + dist[k][j] < dist[i][j])
                {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }

    printf("\nShortest Distance Matrix :\n");

    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (dist[i][j] == 999)
                printf("INF ");
            else
                printf("%3d ", dist[i][j]);
        }
        printf("\n");
    }

    return 0;
}
```

### Example

Input:

```
Enter Number Of Vertices : 4
Enter Adjacency Matrix :
0 5 999 10
999 0 3 999
999 999 0 1
999 999 999 0
```

Output:

```
Shortest Distance Matrix :
  0   5   8   9
INF   0   3   4
INF INF   0   1
INF INF INF   0
```
