using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    //Este script se usa para controlar las cameras
    //Cada agente tiene una camara, y esta la camara principal
    //La idea es que la camara principal se pueda rotar con W,A,S,D,Q,E, y 
    public Camera mainCamera;
    public List<Camera> agentCameras = new List<Camera>();
    private int currentCameraIndex = 0;
    public float moveSpeed = 5.0f;
    public float rotationSpeed = 30.0f;

    void Start()
    {
        mainCamera.enabled = true;
        DeactivateAllAgentCameras();
    }

    void Update()
    {
        Robot[] allRobots = GameObject.FindObjectsOfType<Robot>();
        Package[] allPackages = GameObject.FindObjectsOfType<Package>();
        
        agentCameras.Clear();  
        foreach (Robot robot in allRobots)
        {
            agentCameras.Add(robot.GetComponentInChildren<Camera>());
        }
        foreach (Package package in allPackages)
        {
            agentCameras.Add(package.GetComponentInChildren<Camera>());
        }

        // Switch to the main camera
        if (Input.GetKeyDown(KeyCode.M))
        {
            DeactivateAllAgentCameras();
            mainCamera.enabled = true;
        }
        
        // Cycle through agent cameras
        else if (Input.GetKeyDown(KeyCode.RightArrow))
        {
            currentCameraIndex++;
            if (currentCameraIndex >= agentCameras.Count)
            {
                currentCameraIndex = 0;
            }
            SwitchToCamera(currentCameraIndex);
        }
        else if (Input.GetKeyDown(KeyCode.LeftArrow))
        {
            currentCameraIndex--;
            if (currentCameraIndex < 0)
            {
                currentCameraIndex = agentCameras.Count - 1;
            }
            Debug.Log("At camera index " + currentCameraIndex);
            SwitchToCamera(currentCameraIndex);
        }

        if (mainCamera.enabled)
        {
            if (Input.GetKey(KeyCode.W))
            {
                mainCamera.transform.position += mainCamera.transform.forward * moveSpeed * Time.deltaTime;
            }
            if (Input.GetKey(KeyCode.S))
            {
                mainCamera.transform.position -= mainCamera.transform.forward * moveSpeed * Time.deltaTime;
            }
            if (Input.GetKey(KeyCode.A))
            {
                mainCamera.transform.position -= mainCamera.transform.right * moveSpeed * Time.deltaTime;
            }
            if (Input.GetKey(KeyCode.D))
            {
                mainCamera.transform.position += mainCamera.transform.right * moveSpeed * Time.deltaTime;
            }
            if (Input.GetKey(KeyCode.Q))
            {
                mainCamera.transform.Rotate(Vector3.up, -rotationSpeed * Time.deltaTime);
            }
            if (Input.GetKey(KeyCode.E))
            {
                mainCamera.transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);
            }
        }
    }

    void SwitchToCamera(int index)
    {
        if (index >= 0 && index < agentCameras.Count)
        {
            DeactivateAllAgentCameras();
            agentCameras[index].enabled = true;
            mainCamera.enabled = false;
        }
    }

    void DeactivateAllAgentCameras()
    {
        foreach (Camera cam in agentCameras)
        {
            cam.enabled = false;
        }
    }
}
