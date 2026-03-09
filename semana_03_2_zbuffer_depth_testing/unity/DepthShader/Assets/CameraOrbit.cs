using UnityEngine;

public class CameraOrbit : MonoBehaviour
{
    [Header("Velocidad de rotación")]
    public float orbitSpeed = 20f;

    void Update()
    {
        // 1. Gira alrededor del centro (0,0,0)
        transform.RotateAround(Vector3.zero, Vector3.up, orbitSpeed * Time.deltaTime);
        
        // 2. Obliga a la cámara a mirar siempre hacia el centro (0,0,0)
        transform.LookAt(Vector3.zero);
    }
}