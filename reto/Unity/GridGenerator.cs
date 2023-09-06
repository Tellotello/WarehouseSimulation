using UnityEngine;

[ExecuteInEditMode] 
public class GridGenerator : MonoBehaviour
{
    //Prefabs
    public GameObject mainCamera;  
    public GameObject floorPrefab; 
    public GameObject shelfPrefab; 

    // Po
    private readonly Vector2Int[][] shelfPositions = new Vector2Int[][] {
        new Vector2Int[] { new Vector2Int(4, 2), new Vector2Int(4, 3), new Vector2Int(4, 4), new Vector2Int(4, 5),
                           new Vector2Int(5, 2), new Vector2Int(5, 3), new Vector2Int(5, 4), new Vector2Int(5, 5) },
        new Vector2Int[] { new Vector2Int(4, 9), new Vector2Int(4, 10), new Vector2Int(4, 11), new Vector2Int(4, 12),
                           new Vector2Int(5, 9), new Vector2Int(5, 10), new Vector2Int(5, 11), new Vector2Int(5, 12) },
        new Vector2Int[] { new Vector2Int(9, 2), new Vector2Int(9, 3), new Vector2Int(9, 4), new Vector2Int(9, 5),
                           new Vector2Int(10, 2), new Vector2Int(10, 3), new Vector2Int(10, 4), new Vector2Int(10, 5) },
        new Vector2Int[] { new Vector2Int(9, 9), new Vector2Int(9, 10), new Vector2Int(9, 11), new Vector2Int(9, 12),
                           new Vector2Int(10, 9), new Vector2Int(10, 10), new Vector2Int(10, 11), new Vector2Int(10, 12) }
    };

     void Start()
    {
        if (mainCamera != null)
        {
            Camera.main.gameObject.SetActive(false); 
            mainCamera.SetActive(true);  
        }

        CreateFloorGrid();
        CreateShelves();
        
    }


    private void CreateFloorGrid()
    {
        for (int x = 0; x <= 14; x++)
        {
            for (int z = 0; z <= 14; z++)
            {
                Vector3 position = new Vector3(x, 0, z);
                Instantiate(floorPrefab, position, Quaternion.identity);
            }
        }
    }

    private void CreateShelves()
    {
        foreach (Vector2Int[] group in shelfPositions)
        {
            foreach (Vector2Int pos in group)
            {
                Vector3 position = new Vector3(pos.x, 0, pos.y);
                Instantiate(shelfPrefab, position, Quaternion.identity);
            }
        }
    }




}
