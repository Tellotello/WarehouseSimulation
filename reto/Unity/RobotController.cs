using UnityEngine;

public class RobotController : MonoBehaviour
{
    public GameObject robot;  
    public float moveAmount = 1f; 
    public float rotateAmount = 45f;  

    void Update()
    {
        Vector3 moveDirection = Vector3.zero;

        if (Input.GetKey(KeyCode.W))
        {
            moveDirection += Vector3.forward;
        }
        if (Input.GetKey(KeyCode.S))
        {
            moveDirection += Vector3.back;
        }
        if (Input.GetKey(KeyCode.A))
        {
            moveDirection += Vector3.left;
        }
        if (Input.GetKey(KeyCode.D))
        {
            moveDirection += Vector3.right;
        }
        if (Input.GetKey(KeyCode.Q))
        {
            robot.transform.Rotate(Vector3.up, -rotateAmount * Time.deltaTime);
        }
        if (Input.GetKey(KeyCode.E))
        {
            robot.transform.Rotate(Vector3.up, rotateAmount * Time.deltaTime);
        }

        if (moveDirection != Vector3.zero)
        {
            robot.transform.position += moveDirection.normalized * moveAmount * Time.deltaTime;
        }
    }
}
