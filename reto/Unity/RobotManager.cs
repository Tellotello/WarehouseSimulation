using System.Collections.Generic;
using UnityEngine;

public class RobotManager : MonoBehaviour
{
    private Dictionary<string, GameObject> robots = new Dictionary<string, GameObject>();
    private Dictionary<string, Vector3> targetPositions = new Dictionary<string, Vector3>();

    public float moveSpeed = 1.0f;

    void Start()
    {
        RegisterAllRobots();
    }

   

  

    private void RegisterAllRobots()
    {
        GameObject[] foundRobots = GameObject.FindGameObjectsWithTag("Robot");
        for (int i = 0; i < foundRobots.Length; i++)
        {
            string robotID = "R" + (i + 1).ToString();
            robots[robotID] = foundRobots[i];
            Debug.Log("Registered robot " + robotID);
        }
    }
}
