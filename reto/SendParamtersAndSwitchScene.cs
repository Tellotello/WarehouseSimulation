using UnityEngine;
using UnityEngine.UI;
using TMPro;  // Add this namespace
using UnityEngine.SceneManagement;
using UnityEngine.Networking;
using System.Collections;
public class StartSimulationButton : MonoBehaviour
{
    public TMP_InputField numRobotsInputField;
    public string apiURL = "http://127.0.0.1:5000/api/params";

    public void StartSimulation()
    {
        string numRobots = numRobotsInputField.text;
        Debug.Log("Sending numRobots: " + numRobots);

        string jsonData = "{\"num_robots\": \"" + numRobots + "\"}";

        PlayerPrefs.SetString("numRobots", numRobotsInputField.text);
        StartCoroutine(PostRequest(apiURL, jsonData));
    }

//A
    IEnumerator PostRequest(string url, string jsonData)
    {
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError)
        {
            Debug.Log("Error: " + request.error);
        }
        else
        {
            Debug.Log("Received: " + request.downloadHandler.text);

            SceneManager.LoadScene("WarehouseScene");
        }
    }
}
