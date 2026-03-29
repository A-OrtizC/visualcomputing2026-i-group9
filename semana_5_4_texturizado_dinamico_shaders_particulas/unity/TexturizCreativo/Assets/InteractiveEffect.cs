using UnityEngine;

public class InteractiveEffect : MonoBehaviour
{
    public Material fluidMaterial;
    public ParticleSystem particles;
    
    [Header("Configuración de Clic")]
    public float clickDistortion = 0.5f;
    public float clickSpeed = 10f;
    public int particleBurstCount = 100;

    private float baseDistortion;
    private float baseSpeed;

    void Start()
    {
        if (fluidMaterial != null)
        {
            baseDistortion = fluidMaterial.GetFloat("_Amount");
            baseSpeed = fluidMaterial.GetFloat("_Speed");
        }
    }

    void Update()
    {
        // Interacción al hacer clic izquierdo
        if (Input.GetMouseButtonDown(0))
        {
            TriggerExplosion();
        }
    }

    void TriggerExplosion()
    {
        if (fluidMaterial != null)
        {
            fluidMaterial.SetFloat("_Amount", clickDistortion);
            fluidMaterial.SetFloat("_Speed", clickSpeed);
            Invoke("ResetMaterial", 0.5f);
        }

        if (particles != null)
        {
            particles.Emit(particleBurstCount);
        }
    }

    void ResetMaterial()
    {
        if (fluidMaterial != null)
        {
            fluidMaterial.SetFloat("_Amount", baseDistortion);
            fluidMaterial.SetFloat("_Speed", baseSpeed);
        }
    }
}