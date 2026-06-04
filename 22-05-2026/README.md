# Programming Exercises - May 22, 2026

## Exercise 1 : Prim's Algorithm

### Question : Write a program to find the Minimum Spanning Tree using Prim's algorithm

### Algorithm

1. Input the number of vertices `n`.
2. Read the adjacency matrix `graph[n][n]` where `0` indicates no edge (or use a sentinel for INF).
3. Initialize a `selected[]` array to mark vertices included in the MST; start with `selected[0] = 1`.
4. Repeat until MST has `n - 1` edges:
   - For every vertex `u` in the selected set, examine all edges `(u, v)` to vertices `v` not yet selected.
   - Pick the smallest-weight edge that connects the selected set to a non-selected vertex.
   - Add that edge to the MST, mark `v` as selected, and add the weight to the total cost.
5. Print the selected edges and the total cost.

### Code

```cpp
#include <stdio.h>

int main()
{
    int n;

    printf("Enter Number Of Vertices : ");
    scanf("%d", &n);

    int graph[n][n];
    int selected[n];

    printf("Enter Adjacency Matrix :\n");
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            scanf("%d", &graph[i][j]);
        }
    }

    for (int i = 0; i < n; i++)
        selected[i] = 0;

    selected[0] = 1; // Start From Vertex 0

    int edges = 0, totalCost = 0;

    printf("\nMinimum Spanning Tree :\n");
    printf("Edge\tWeight\n");

    while (edges < n - 1)
    {
        int min = 9999;
        int x = -1, y = -1;

        for (int i = 0; i < n; i++)
        {
            if (selected[i])
            {
                for (int j = 0; j < n; j++)
                {
                    if (!selected[j] && graph[i][j] != 0)
                    {
                        if (graph[i][j] < min)
                        {
                            min = graph[i][j];
                            x = i;
                            y = j;
                        }
                    }
                }
            }
        }

        printf("%d - %d\t%d\n", x, y, min);

        totalCost += min;
        selected[y] = 1;
        edges++;
    }

    printf("Total Cost = %d\n", totalCost);

    return 0;
}
```

### Example

Input:

```
Enter Number Of Vertices : 4
Enter Adjacency Matrix :
0 2 0 6
2 0 3 8
0 3 0 0
6 8 0 0
```

Output:

```
Minimum Spanning Tree :
Edge	Weight
0 - 1	2
1 - 2	3
0 - 3	6
Total Cost = 11
```
