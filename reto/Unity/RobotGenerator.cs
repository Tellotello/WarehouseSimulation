using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RobotGenerator : MonoBehaviour
{
    public GameObject robotPrefab; 
    private Dictionary<int, GameObject> robotMap = new Dictionary<int, GameObject>();

    private void CreateRobots(int numRobots)
    {
        int robotsCreated = 0;
        int nextRobotID = 0;  

        for (int x = 0; x <= 14; x++)
        {
            for (int z = 0; z <= 7; z++)
            {
                if (robotsCreated >= numRobots)
                {
                    return; // 
                }

                Vector3 position = new Vector3(x, 0, z);
                GameObject newRobot = Instantiate(robotPrefab, position, Quaternion.identity);

             
                newRobot.GetComponent<Robot>().ID = nextRobotID;
                Debug.Log("Created robot with ID: " + nextRobotID);
                robotMap.Add(nextRobotID, newRobot);
                nextRobotID++;

                robotsCreated++;
            }
        }
    }

    void Start()
    {
        int num_robots;
        if (int.TryParse(PlayerPrefs.GetString("numRobots"), out num_robots))
        {
        }
        else
        {
           
            num_robots = 0;
        }

        CreateRobots(num_robots);
    }

    void Update()
    {
        
    }
}
