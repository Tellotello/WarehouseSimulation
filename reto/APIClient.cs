using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using SimpleJSON;
using System.Linq;

public class APIClient : MonoBehaviour
{

    //Este script es que recibe los datos del apiy se encarga de hacer todos los movimientos de los agentes
    private string apiURL = "http://127.0.0.1:5000/api/update";
    public float updateInterval = 1.0f;
    public float moveSpeed = 10.0f;  //Velocidad de movimiento

    //Change this to be an array of prefabs

    //Array of prefabs
    public GameObject[] packagePrefabs = new GameObject[7]; // Prefabs de los paquetes

   

    

    private Dictionary<string, GameObject> packageDictionary = new Dictionary<string, GameObject>(); // Diccionario que guarda los paquetes
    private Dictionary<string, Vector3> targetPositions = new Dictionary<string, Vector3>();  // Diccionario que guarda las posiciones de los agentes

    private bool isStepComplete = true;

    void Start()
    {
        StartCoroutine(GetAgentData()); // Inicia la corrutina
    }

    void Update()
    {
        foreach (var kvp in targetPositions) // Recorre el diccionario de posiciones
        {
            string id = kvp.Key; // ID del agente
            Vector3 targetPosition = kvp.Value; // Posicion del agente

            GameObject agent;
            if (packageDictionary.TryGetValue(id, out agent)) // Si el agente es un paquete
            {
                // For packages
                if(targetPosition.x >12) // Para destruir el paquete
                {
                    agent.GetComponent<Renderer>().enabled = false;
                }
                else{
                    agent.transform.position = Vector3.MoveTowards(agent.transform.position, targetPosition, moveSpeed * Time.deltaTime); // Mueve el paquete

                }
            }
            else
            {
                // Para los robots
                Robot robotScript = System.Array.Find(GameObject.FindObjectsOfType<Robot>(), r => r.ID.ToString() == id); // Busca el robot con el ID
                if (robotScript != null) // Si el robot existe
                {
                    robotScript.gameObject.transform.position = Vector3.MoveTowards( // Mueve el robot
                        robotScript.gameObject.transform.position,
                        targetPosition,
                        moveSpeed * Time.deltaTime
                    );
                }
            }
        }
    }

    IEnumerator GetAgentData() // Corrutina que recibe los datos del api
    {
        int lastStep = -1;
        GameObject packageToUse; // Prefab del paquete

        while (true) // Mientras el juego este corriendo
        {
            if (isStepComplete) // Si el paso esta completo
            {
                UnityWebRequest request = UnityWebRequest.Get(apiURL); // Hace la peticion al api
                yield return request.SendWebRequest(); // Espera la respuesta

                if (request.result == UnityWebRequest.Result.ConnectionError) // Si hay error
                {
                    //Debug.Log("Error: " + request.error);
                }
                else
                {
                    JSONNode jsonResponse = JSON.Parse(request.downloadHandler.text); // Obtiene la respuesta
                   // Debug.Log("Received: " + jsonResponse.ToString());

                    int currentStep = jsonResponse["step"]; // Obtiene el paso actual

                    if (currentStep != lastStep) // Si el paso actual es diferente al anterior
                    {
                        lastStep = currentStep;

                        Robot[] allRobots = GameObject.FindObjectsOfType<Robot>(); // Busca todos los robots
                        JSONNode agents = jsonResponse["agents"]; // Obtiene los agentes

                        foreach (string id in agents.Keys) // Recorre los agentes
                        { 
                            float x = agents[id]["x"]; // Obtiene la posicion del agente
                            float y = agents[id]["y"];
                           // float z = agents[id]["z"];

                            if (agents[id]["type"] == "Robot") // Si el agente es un robot
                            {
                                foreach (Robot robotScript in allRobots) // Recorre los robots
                                {
                                    if (robotScript.ID.ToString() == id) // Si el ID del robot es igual al ID del agente
                                    {
                                        //Debug.Log("Robot " + id + " is at " + x + ", " + y);
                                        targetPositions[id] = new Vector3(x, 0, y);  // Actualiza la posicion del robot
                                        //Debug.Log("Robot " + id + " is moving to " + x + ", " + y);
                                    }
                                }
                            }
                            else if (agents[id]["type"] == "Package")
                            {
                                GameObject existingPackage;
                                if (packageDictionary.TryGetValue(id, out existingPackage))
                                {
                                    // Actualiza la posicion del paquete
                                  //  Debug.Log("Package " + id + " is at " + x + ", " + y+ ", " + z  );
                                    targetPositions[id] = new Vector3(x, 1, y);
                                   // Debug.Log("Package " + id + " is moving to " + x + ", " + y);
                                }
                                else
                                {
                                      if (currentStep >= 0)
                                    {
                                        int packagePrefabToUse = Random.Range(0, 7); // Elige un prefab aleatorio
                                        packageToUse = packagePrefabs[packagePrefabToUse]; // Obtiene el prefab
                                        GameObject newPackage = Instantiate(packageToUse, new Vector3(x, 1, y), Quaternion.identity); // Instancia el paquete
                                        packageDictionary.Add(id, newPackage); // Agrega el paquete al diccionario
 
                                        Package packageScript = newPackage.GetComponent<Package>(); // Obtiene el script del paquete
                                        packageScript.ID = int.Parse(id); // Actualiza el ID del paquete
                                        targetPositions[id] = new Vector3(x, 1, y); // Actualiza la posicion del paquete
                                    }
                                }
                            }
                        }

                        isStepComplete = true;  // Actualiza el paso
                    }
                }
            }

            yield return new WaitForSeconds(updateInterval); // Espera el intervalo de actualizacion
        }
    }
}
