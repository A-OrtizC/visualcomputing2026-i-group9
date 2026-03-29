using UnityEngine;
using UnityEngine.UI;

public class LightController : MonoBehaviour
{
    [Header("Configuración de Luz")]
    public Light directionalLight;
    public Slider intensitySlider;

    void Start()
    {
        // Si no se asignó la luz, busca la luz principal de la escena
        if (directionalLight == null)
        {
            directionalLight = RenderSettings.sun;
        }
            
        // Sincronizar el valor inicial del slider con la luz
        if (directionalLight != null && intensitySlider != null)
        {
            intensitySlider.value = directionalLight.intensity;
            intensitySlider.onValueChanged.AddListener(UpdateLightIntensity);
        }
    }

    // Se ejecuta cada vez que mueves el slider
    void UpdateLightIntensity(float value)
    {
        if (directionalLight != null)
        {
            directionalLight.intensity = value;
        }
    }
}