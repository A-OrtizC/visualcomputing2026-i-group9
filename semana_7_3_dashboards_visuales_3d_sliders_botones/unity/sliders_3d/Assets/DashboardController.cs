using UnityEngine;
using UnityEngine.UI; // Requerido para acceder a Slider y Button

public class DashboardController : MonoBehaviour
{
    [Header("Referencias 3D")]
    public GameObject targetObject;       // Objeto a transformar (Cubo)
    public Light directionalLight;        // Luz a modificar

    [Header("Referencias UI")]
    public Slider scaleSlider;
    public Slider lightSlider;
    public Button colorButton;
    public Button rotateButton;

    // Bandera para la transformación en el tiempo
    private bool isRotating = false;
    private Renderer targetRenderer;

    void Start()
    {
        // Cachear el renderer para modificar el pipeline de material
        if (targetObject != null)
        {
            targetRenderer = targetObject.GetComponent<Renderer>();
            // Inicializar slider con la escala actual (matriz S)
            scaleSlider.value = targetObject.transform.localScale.x;
        }

        if (directionalLight != null)
        {
            lightSlider.value = directionalLight.intensity;
        }

        // Suscripción a eventos de UI (Delegados)
        scaleSlider.onValueChanged.AddListener(UpdateScale);
        lightSlider.onValueChanged.AddListener(UpdateLight);
        colorButton.onClick.AddListener(ChangeRandomColor);
        rotateButton.onClick.AddListener(ToggleRotation);
    }

    void Update()
    {
        // Aplicación de rotación continua independiente del framerate (Euler angles)
        if (isRotating && targetObject != null)
        {
            targetObject.transform.Rotate(Vector3.up * 60f * Time.deltaTime, Space.World);
            targetObject.transform.Rotate(Vector3.right * 30f * Time.deltaTime, Space.World);
        }
    }

    void UpdateScale(float newScale)
    {
        // Escala uniforme: S(sx, sy, sz) donde sx = sy = sz = newScale
        targetObject.transform.localScale = new Vector3(newScale, newScale, newScale);
    }

    void UpdateLight(float newIntensity)
    {
        directionalLight.intensity = newIntensity;
    }

    void ChangeRandomColor()
    {
        if (targetRenderer != null)
        {
            // Modifica el color difuso base del material asignado
            targetRenderer.material.color = Random.ColorHSV(0f, 1f, 0.8f, 1f, 0.8f, 1f);
        }
    }

    void ToggleRotation()
    {
        isRotating = !isRotating; // Invierte el estado booleano
    }
}