using UnityEngine;
using UnityEngine.UI;

public class MaterialController : MonoBehaviour
{
    public Material pbrMaterial;
    public Slider metallicSlider;
    public Slider smoothnessSlider;

    // Esta función la llamaremos directamente desde el Slider
    public void UpdateMaterialValues()
    {
        if (pbrMaterial != null)
        {
            // Forzamos el valor del slider al material
            pbrMaterial.SetFloat("_Metallic", metallicSlider.value);
            
            // Intentamos ambos nombres comunes por si acaso
            pbrMaterial.SetFloat("_Glossiness", smoothnessSlider.value);
            pbrMaterial.SetFloat("_Smoothness", smoothnessSlider.value);
            
            Debug.Log("Actualizando: M=" + metallicSlider.value + " S=" + smoothnessSlider.value);
        }
    }
}