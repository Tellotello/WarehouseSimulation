using UnityEngine;

[ExecuteInEditMode] 
public class SetMainCameraInEditMode : MonoBehaviour
{
    public GameObject cameraToBeMain;  

    void Start()
    {
        SetCamera();
    }

    void Update()
    {
         SetCamera();
    }

    void SetCamera()
    {
        if (cameraToBeMain != null && cameraToBeMain.GetComponent<Camera>() != null)
        {
            if (Camera.main != null)
            {
                Camera.main.gameObject.SetActive(false);
            }

            cameraToBeMain.SetActive(true);

            cameraToBeMain.tag = "MainCamera";
        }
        else
        {
            Debug.LogError("cameraToBeMain GameObject is either null or does not have a Camera component.");
        }
    }
}
