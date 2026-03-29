using UnityEngine;

public class ColorCycle : MonoBehaviour
{
    // Referencias a los componentes que cambian de color
    private Renderer sphereRenderer;
    private Renderer cubeRenderer;

    void Start()
    {
        // Obtenemos los componentes Renderer de los objetos hijos o del mismo objeto
        // Para este ejemplo, asumiremos que el script se pone directamente en el objeto
        sphereRenderer = GetComponent<Renderer>();
    }

    void Update()
    {
        // Calculamos el matiz (Hue) basado en el tiempo para que cicle constantemente
        // El valor oscila entre 0 y 1
        float hue = Mathf.PingPong(Time.time * 0.5f, 1f);
        
        // Convertimos HSV a RGB (Saturación y Brillo al máximo para que resalte)
        Color newColor = Color.HSVToRGB(hue, 1f, 1f);
        
        // Aplicamos el color al material
        sphereRenderer.material.color = newColor;
    }
}