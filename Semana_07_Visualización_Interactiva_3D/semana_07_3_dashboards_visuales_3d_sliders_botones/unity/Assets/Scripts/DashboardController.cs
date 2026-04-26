using UnityEngine;
using UnityEngine.UI;

public class DashboardController : MonoBehaviour
{
    [Header("Escena 3D")]
    public GameObject targetObject;
    public Light directionalLight;

    [Header("Controles UI")]
    public Slider scaleSlider;
    public Slider lightSlider;
    public Button colorButton;
    public Button rotateButton;

    private bool isRotating = false;

    void Start()
    {
        // 1. Inicializar valores de los sliders según el estado actual de la escena
        if (targetObject != null) scaleSlider.value = targetObject.transform.localScale.x;
        if (directionalLight != null) lightSlider.value = directionalLight.intensity;

        // 2. Conectar eventos UI con funciones
        scaleSlider.onValueChanged.AddListener(UpdateScale);
        lightSlider.onValueChanged.AddListener(UpdateLight);
        colorButton.onClick.AddListener(ChangeRandomColor);
        rotateButton.onClick.AddListener(ToggleRotation);
    }

    void Update()
    {
        if (isRotating && targetObject != null)
        {
            // Transformación rotacional continua independiente del framerate
            targetObject.transform.Rotate(Vector3.up * 60f * Time.deltaTime, Space.World);
            targetObject.transform.Rotate(Vector3.right * 30f * Time.deltaTime, Space.World);
        }
    }

    void UpdateScale(float value)
    {
        // Matriz de transformación de escala uniforme
        targetObject.transform.localScale = new Vector3(value, value, value);
    }

    void UpdateLight(float value)
    {
        directionalLight.intensity = value;
    }

    void ChangeRandomColor()
    {
        Renderer renderer = targetObject.GetComponent<Renderer>();
        if (renderer != null)
        {
            // Cambiar color difuso del material actual
            renderer.material.color = Random.ColorHSV(0f, 1f, 0.8f, 1f, 0.8f, 1f);
        }
    }

    void ToggleRotation()
    {
        isRotating = !isRotating;
    }
}
